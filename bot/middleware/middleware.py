import sqlite3
import os
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from dotenv import load_dotenv

from models import model
from db import get_group, DbConnection


load_dotenv()




class GroupMiddleware(BaseMiddleware):

    def __check_group(self, event: TelegramObject) -> model.Group:
        with DbConnection() as db_conn:
            return get_group(db_conn, event.chat.id)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:

        data['group'] = self.__check_group(event)

        result = await handler(event, data)
        return result