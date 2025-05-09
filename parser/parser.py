import asyncio
import os
import re
import sqlite3
from urllib.parse import urljoin, urlparse, unquote
import log

from dotenv import load_dotenv
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from aiogram import Bot
from aiogram.types import FSInputFile
from aiogram.exceptions import TelegramBadRequest

from utils import file_hash, Link, FormaObychenia, File, GroupNotify
from db import save_schedule_file, update_schedule_file, get_hash_by_url


load_dotenv()


BASE_URL = os.environ['BASE_URL']
LOGIN_PATH = os.environ['LOGIN_PATH']
STORAGE_CHAT_ID = os.environ['STORAGE_CHAT_ID']
BOT_TOKEN = os.environ['BOT_TOKEN']


#
async def download_files(
        db_conn: sqlite3.Connection,
        session: ClientSession,
        links: list[Link],
        dest_folder: str = os.environ['DOWNLOAD_DIR'],

) -> list[File]:
    os.makedirs(dest_folder, exist_ok=True)
    saved_paths = []

    for link in links:

        async with session.get(link.url) as resp:
            resp.raise_for_status()
            cd = resp.headers.get('Content-Disposition', '')
            filename = None
            if cd:
                m = re.search(r"filename\*?=(?:UTF-8''?)?['\"]?(.*?)(?=['\";]|$)", cd)
                if m:
                    filename = unquote(m.group(1))
            if not filename:
                filename = unquote(os.path.basename(urlparse(link.url).path)) or 'file'

            filepath = os.path.join(dest_folder, filename)
            ctype = resp.headers.get('Content-Type', '')
            if any(sub in ctype for sub in ('text/', 'application/json', 'application/xml', 'text/calendar')):
                text = await resp.text()
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(text)
            else:
                data = await resp.read()
                with open(filepath, 'wb') as f:
                    f.write(data)

            # Если расписание с таким url уже есть в бд, то нужно чекнуть их hash
            temp_file_hash = get_hash_by_url(db_conn, url=link.url)
            current_hash = file_hash(filepath)
            file = None
            if temp_file_hash:
                if temp_file_hash == current_hash:
                    log.logger.info(f'файл {filepath} уже находится в бд, hash: {temp_file_hash}')
                    os.remove(filepath)
                    continue

                file = File(filepath, file_hash(filepath), link, updated=True)  # Расписание на этот период изменилось

            if file is None:
                file = File(filepath, file_hash(filepath), link)

        saved_paths.append(file)

    return saved_paths


async def upload_new_files(
        db_conn: sqlite3.Connection,
        bot: Bot,
        files: list[File]
) -> list[File]:

    for file in files:
        filename = os.path.basename(file.path)
        try:
            sent = await bot.send_document(
                chat_id=STORAGE_CHAT_ID,
                document=FSInputFile(file.path),
                disable_notification=True
            )
            file.set_file_id(sent.document.file_id)
            await bot.delete_message(chat_id=STORAGE_CHAT_ID, message_id=sent.message_id)

        except TelegramBadRequest as e:
            log.logger.error(f'Ошибка при загрузке {filename}: {e}')
    return files


async def clear_folder_downloads():
    try:
        for filename in os.listdir(os.environ['DOWNLOAD_DIR']):
            os.remove(os.path.join(os.environ['DOWNLOAD_DIR'], filename))
        log.logger.info(f"Очищена папка {os.environ['DOWNLOAD_DIR']}")
    except Exception as e:
        log.logger.error(f"Ошибка при очистке папки {os.environ['DOWNLOAD_DIR']}: {e}")


async def fetch_csrf_and_action(session: ClientSession) -> tuple[dict, str]:
    login_url = urljoin(BASE_URL, LOGIN_PATH)
    async with session.get(login_url) as resp:
        resp.raise_for_status()
        html = await resp.text()

    soup = BeautifulSoup(html, 'html.parser')
    form = soup.find('form', id='com-users-login__form')
    if not form:
        raise RuntimeError("Не найдена форма логина на странице")

    payload = {inp['name']: inp.get('value', '') for inp in form.find_all('input', type='hidden')}
    action_url = urljoin(BASE_URL, form['action'])
    return payload, action_url


async def login(username: str, password: str) -> ClientSession:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 Edg/92.0.902.67',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    }
    session = ClientSession(headers=headers)
    try:
        payload, post_url = await fetch_csrf_and_action(session)
        print(f"FORM-URL: {post_url}")
        payload.update({'username': username, 'password': password, 'remember': 'yes'})
        session.headers.update({'Referer': urljoin(BASE_URL, LOGIN_PATH)})

        async with session.post(post_url, data=payload) as login_resp:
            text = await login_resp.text()
            if login_resp.status != 200 or 'Выйти' not in text:
                raise RuntimeError('Авторизация не удалась — проверьте логин/пароль и CSRF-поля')
    except Exception:
        await session.close()
        raise
    log.logger.info("Session got")
    return session


async def fetch_and_extract_links_ochnaya_forma(session: ClientSession) -> list[Link]:
    """
    Получаем ссылки на скачивания расписания для очной формы
    :param session:
    :return:
    """
    url = urljoin(BASE_URL, "/schedule/ochnaya-forma")
    async with session.get(url) as resp:
        resp.raise_for_status()
        html = await resp.text()

    soup = BeautifulSoup(html, 'html.parser')
    panels = soup.select('div.uk-panel.uk-margin')
    links = []
    for panel in panels:
        for a in panel.find_all('a', href=True):
            href = a['href']
            full = urljoin(BASE_URL, href)
            link_temp = Link(url=full, forma=FormaObychenia.OCHNO.value)
            if href.startswith('/images/uo/OFO/1k'):
                link_temp.kyrs = 1
            elif href.startswith('/images/uo/OFO/2k'):
                link_temp.kyrs = 2
            elif href.startswith('/images/uo/OFO/3k'):
                link_temp.kyrs = 3
            elif href.startswith('/images/uo/OFO/4k'):
                link_temp.kyrs = 4
            else:
                continue
            links.append(link_temp)
    return links


async def fetch_and_extract_links_och_zaoch_forma(session: ClientSession) -> list[Link]:
    """
    Получаем ссылки на скачивания расписания для очно-заочной формы
    :param session:
    :return:
    """
    url = urljoin(BASE_URL, "/schedule/och-zaoch-forma")
    async with session.get(url) as resp:
        resp.raise_for_status()
        html = await resp.text()

    soup = BeautifulSoup(html, 'html.parser')
    panels = soup.select('div.uk-panel.uk-margin')
    links = []
    for panel in panels:
        for a in panel.find_all('a', href=True):
            href = a['href']
            full = urljoin(BASE_URL, href)
            link_temp = Link(url=full, forma=FormaObychenia.OCHNO_AND_ZA_OCHNO.value)
            if href.startswith('/images/uo/OZFO/1k'):
                link_temp.kyrs = 1
            elif href.startswith('/images/uo/OZFO/2k'):
                link_temp.kyrs = 2
            elif href.startswith('/images/uo/OZFO/3k'):
                link_temp.kyrs = 3
            elif href.startswith('/images/uo/OZFO/4k'):
                link_temp.kyrs = 4
            else:
                continue
            links.append(link_temp)
    return links


async def save_data(db_conn: sqlite3.Connection, files: list[File]):
    for file in files:
        if file.updated:

            update_schedule_file(db_conn, file)
            log.logger.info(f"Обновлен файл, hash: {file.hash}; file_id: {file.file_id} ")
        else:
            save_schedule_file(db_conn, file)


async def get_groups_notify(db_conn: sqlite3.Connection, file_type: int, file_id: str) -> list[GroupNotify]:

    cursor = db_conn.cursor()
    try:
        query = """
            SELECT 
                chat_id
            FROM
                TgGroup
            WHERE
                isActivated = ?
              AND isNotify = ?
              AND ref_file_type = ?;
        
        """
        res = []
        cursor.execute(query, (True, True, file_type, ))
        for row in cursor.fetchall():
            res.append(
                GroupNotify(
                    chat_id=row[-1],
                    file_id=file_id
                )
            )

        return res

    finally:
        if cursor:
            cursor.close()


async def send_notify(db_conn: sqlite3.Connection, bot: Bot, files: list[File]):

    groups: list[GroupNotify] = []
    for file in files:
        groups += await get_groups_notify(db_conn, file.link.file_type, file.file_id)

    for group in groups:
        await bot.send_document(
            chat_id=group.chat_id,
            document=group.file_id,
            caption="Выложено новое расписание!"
        )


async def main():
    session = None
    db = None
    bot = Bot(token=BOT_TOKEN)
    while True:
        try:
            db = sqlite3.connect(os.environ['DATABASE'])
            session = await login(os.environ['USERNAME_MISIS'], os.environ['PASSWORD_MISIS'])

            funcs = {
                "och": fetch_and_extract_links_ochnaya_forma,
                "och_zaoch": fetch_and_extract_links_och_zaoch_forma
            }

            links = {
                forma_ob: await func(session) for forma_ob, func in funcs.items()
            }

            files = {
                forma_ob: await download_files(db, session, links) for forma_ob, links in links.items()
            }

            uploaded_files = {
                forma_ob: await upload_new_files(db, bot, files) for forma_ob, files in files.items()
            }

            for_notify = []
            for _, files in uploaded_files.items():
                for_notify += files
                await save_data(db, files)

            await send_notify(db, bot, for_notify)
            log.logger.info(f"{uploaded_files}")

        except Exception as ex:
            log.logger.error(f"Произошла ошибка {ex}")
        finally:
            if session:
                await session.close()
            db.commit()
            db.close()
            await clear_folder_downloads()

        await asyncio.sleep(300)


if __name__ == '__main__':
    asyncio.run(main())
