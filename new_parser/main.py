import asyncio
import os
import re
import sqlite3
from urllib.parse import urljoin, urlparse, unquote
import log
from subprocess import TimeoutExpired, CalledProcessError
from threading import Thread
from queue import Queue

from dotenv import load_dotenv
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from aiogram import Bot
from aiogram.types import FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.exceptions import TelegramBadRequest


from models import Link, File, FormaObychenia, Event
from utils import file_hash, get_parity_from_excel
from pdf import convert_excel_to_pdf
from jpg import convert_pdf_to_jpgs
from db import (
    get_schedule_info,
    save_schedule_info,
    update_schedule_info,
    find_schedule_info_by_hash_and_url,
    get_subscribes_by_course
                )
from notify_tg import NotifyTelegram


load_dotenv("../.env")


BASE_URL = os.environ['BASE_URL']
LOGIN_PATH = os.environ['LOGIN_PATH']
STORAGE_CHAT_ID = os.environ['STORAGE_CHAT_ID']
NOTIFY_CHAT_ID = os.environ['NOTIFY_CHAT_ID']
BOT_TOKEN = os.environ['BOT_TOKEN']
PDF_DIR = os.environ['PDF_DIR']
JPG_DIR = os.environ['JPG_DIR']
DB_NAME = os.environ['DB_NAME']


queue_message = Queue()


async def main_thread():
    # TODO добавить доотправку
    bot = Bot(BOT_TOKEN)
    while True:
        await asyncio.sleep(6)

        message: tuple[int, str] = queue_message.get(block=True)
        print(message)
        try:
            await bot.send_message(
                chat_id=message[0],
                text=message[1]
            )
        except:
            print("ошибка при отправке сообщения")
            continue



def notify_thread():
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)

    new_loop.run_until_complete(main_thread())




async def download_excels(
        session: ClientSession,
        links: list[Link],
        cursor: sqlite3.Cursor,
        dest_folder: str = os.environ['DOWNLOAD_DIR'],


) -> list[File]:
    os.makedirs(dest_folder, exist_ok=True)
    files = []

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

            parity = get_parity_from_excel(filepath)
            link.parity = parity
            hash_file = file_hash(filepath)
            is_founded = bool(find_schedule_info_by_hash_and_url(hash_excel=hash_file, url=link.url, cur=cursor))

            if is_founded:
                log.logger.info(f"Файл уже есть в бд {link.url}")
                continue



            files.append(File(
                path=filepath,
                link=link,
                _hash=hash_file
            ))

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


async def fetch_and_extract_links_ochnaya_forma(session: ClientSession, expressions: list[str]) -> list[Link]:
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
            flag = False
            for expression in expressions:
                if expression in full:
                    flag = True
                    break

            if flag: continue

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


async def load_jpgs_to_telegram(bot: Bot, caption: str, paths_jpgs: list[str]) -> list[str]:

    # В медиа группу я добавил, ибо мне так удобно ;9
    media_group = MediaGroupBuilder(caption=caption)

    for path in paths_jpgs:
        media_group.add_photo(media=FSInputFile(path))

    result = await bot.send_media_group(chat_id=STORAGE_CHAT_ID, media=media_group.build())

    result = [res.photo[-1].file_id for res in result]
    return result




async def main():
    session = None



    bot = Bot(token=BOT_TOKEN)
    notify_tg = NotifyTelegram(bot=bot, chat_id=int(NOTIFY_CHAT_ID))
    db_connection = sqlite3.connect(DB_NAME)

    while True:
        flag_notify = False
        try:
            try:
                session = await login(os.environ['USERNAME_MISIS'], os.environ['PASSWORD_MISIS'])
            except Exception:
                await notify_tg.send_notify(
                    message="Не получилось пройти авторизацию на сайте Мисиса.",
                    type_message="CRITICAL",
                )
                flag_notify = True
                raise
            funcs = {
                "och": fetch_and_extract_links_ochnaya_forma,
            }

            links = {
                forma_ob: await func(session, [
                    "planovoe"
                ]) for forma_ob, func in funcs.items()
            }

            try:
                cursor = db_connection.cursor()
                execl_files = await download_excels(session, links.get('och'), cursor)
            except Exception as exp:
                await notify_tg.send_notify(
                    message="Не получилось подгрузить таблицы с сайта Мисиса.",
                    type_message="CRITICAL",
                )
                flag_notify = True
                raise
            finally:
                cursor.close()

            pdf_files: list[File] = []

            try:

                for file_excel in execl_files:
                    old_path = file_excel.path
                    file_excel.path = convert_excel_to_pdf(file_excel.path, PDF_DIR)
                    if file_excel.path:
                        pdf_files.append(file_excel)
                    os.remove(old_path)

            except TimeoutExpired:
                await notify_tg.send_notify(
                    message="Ошибка при конвертации таблицы в pdf TIMEOUT.",
                    type_message="CRITICAL",
                )
                flag_notify = True
                raise

            except CalledProcessError:
                await notify_tg.send_notify(
                    message="Ошибка при конвертации таблицы в pdf EXITCODE NOT ZERO.",
                    type_message="CRITICAL",
                )
                flag_notify = True
                raise

            temp_list: list = []
            for i, pdf_file in enumerate(pdf_files):
                try:
                    jpgs = convert_pdf_to_jpgs(pdf_file.path, JPG_DIR, dpi=350, suffix=f"file_number_{i}")
                    if jpgs:
                        temp_list.append(
                            [
                                pdf_file,
                                jpgs
                            ]
                        )
                except Exception:
                    await notify_tg.send_notify(
                        message="Ошибка при конвертации pdf в jpg.",
                        type_message="CRITICAL",
                    )
                    flag_notify = True
                    raise
                finally:
                    os.remove(pdf_file.path)

            events: list[Event] = []
            try:
                for pdf_file, jpgs in temp_list:
                    files_id: list[str] = await load_jpgs_to_telegram(
                        bot,
                        caption=f"Расписание: {pdf_file.link.kyrs} курса, четность: {pdf_file.link.parity}",
                        paths_jpgs=jpgs
                    )

                    try:
                        cursor = db_connection.cursor()
                        event = save_schedule_info(file=pdf_file, files_id=files_id, cur=cursor)
                        events.append(event)
                        db_connection.commit()
                    finally:
                        cursor.close()
                    await asyncio.sleep(25) #  против флуда
            except Exception:
                await notify_tg.send_notify(
                    message="Ошибка при сохранении расписания в бд.",
                    type_message="CRITICAL",
                )
                flag_notify = True
                raise

            try:
                cursor = db_connection.cursor()
                for event in events:
                    chat_ids: list[int] = get_subscribes_by_course(event.course, cursor)
                    message = ""
                    if event.type == "save":
                        message = (f"Было ВЫГРУЖЕНО новое расписание для {event.course} курса, "
                                   f"{'НЕЧЕТНАЯ НЕДЕЛЯ' if event.parity else 'ЧЕТНАЯ НЕДЕЛЯ'}")

                    elif event.type == "update":
                        message = (f"Расписание было ОБНОВЛЕНО {event.course} курса, "
                                   f"{'НЕЧЕТНАЯ НЕДЕЛЯ' if event.parity else 'ЧЕТНАЯ НЕДЕЛЯ'}")

                    for chat_id in chat_ids:
                        queue_message.put((chat_id, message))
            except Exception:
                flag_notify = True
                await notify_tg.send_notify(
                    message=f"Произошла ошибка при рассылке",
                    type_message="MEDIUM_ERROR",
                )
                raise

            finally:
                cursor.close()



        except Exception as ex:
            log.logger.error(f"Произошла ошибка {ex}")
            if not flag_notify:
                await notify_tg.send_notify(
                    message=f"Неизвестная ошибка {ex}",
                    type_message="UNKNOWN_ERROR_TYPE",
                )
        finally:
            if session:
                await session.close()

        await asyncio.sleep(300)


if __name__ == '__main__':
    thread_notify = Thread(
        target=notify_thread,
    )
    thread_notify.start()
    asyncio.run(main())