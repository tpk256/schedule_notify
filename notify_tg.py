import asyncio
import datetime

from aiogram import Bot





class NotifyTelegram:
    def __init__(self, bot: Bot, chat_id: int):
        self.bot = bot
        self.chat_id = chat_id

    async def send_notify(
            self,
            message: str,
            type_message: str,
    ):
        await self.bot.send_message(
            chat_id=self.chat_id,
            text=f"Тип уведомления: {type_message}\n"
                 f"Текст уведомления: {message}\n"
                 f"Дата и время: {datetime.datetime.now()}\n"
        )

