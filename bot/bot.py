import asyncio
import logging
import os
import notify_tg



from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from handlers import router_menu, router_schedule, router_subscribe


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv("../.env")

bot = Bot(token=os.environ['BOT_TOKEN'])


async def main() -> None:

    notify = notify_tg.NotifyTelegram(bot=bot, chat_id=int(os.environ['NOTIFY_CHAT_ID']))
    dp = Dispatcher()
    dp.include_routers(router_schedule, router_subscribe, router_menu)

    try:
        await dp.start_polling(bot)

    except Exception as e:
        await notify.send_notify(
            message=f"Ошибка с ботом {e}",
            type_message="ERROR WITH BOT"
        )
    finally:
        await bot.session.close()

if __name__ == '__main__':

    asyncio.run(main())
