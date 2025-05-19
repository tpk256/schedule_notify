import sqlite3
import os

from models import model


class DbConnection:
    def __enter__(self):
        self.db_conn = sqlite3.connect(os.environ['DATABASE'])
        return self.db_conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db_conn.commit()
        self.db_conn.close()


def activate_group(db_conn: sqlite3.Connection, tg_chat_id: int):
    cursor = db_conn.cursor()

    try:
        query = """
            UPDATE 
                TgGroup
            SET
                is_activated = ?
            WHERE 
                tg_chat_id = ?
        """
        cursor.execute(query, (True, tg_chat_id))

    finally:
        if cursor:
            cursor.close()


def get_edu_groups_id_by_chat_id(db_conn: sqlite3.Connection, tg_chat_id: int) -> list[int]:
    cursor = db_conn.cursor()

    try:
        query = """
            SELECT 
                EduGroup.id,
                EduGroup.edu_group_name
            FROM 
                TgEdu
            JOIN 
                EduGroup ON TgEdu.edu_id = EduGroup.id
            WHERE 
                TgEdu.tg_group_id = ?
        """
        cursor.execute(query, (tg_chat_id,))

        # Извлекаем только имена групп

        return cursor.fetchall()

    finally:
        if cursor:
            cursor.close()


def get_group(db_conn: sqlite3.Connection, tg_chat_id: int) -> model.Group:
    cursor = db_conn.cursor()

    try:
        query = """
             SELECT 
                tg_chat_id,
                tg_group_name,
                is_notify,
                is_activated,
                code_id
            FROM 
                TgGroup
            WHERE
                tg_chat_id = ?;
  
        """
        cursor.execute(query, (tg_chat_id,))
        data = cursor.fetchone()
        if not data:
            return None

        cursor.execute("""
            SELECT 
                code
            FROM 
                Code
            WHERE
                id = ?;
        """, (data[-1], ))
        code = cursor.fetchone()[-1]

        return model.Group(
            chat_id=data[0],
            tg_group_name=data[1],
            is_notify=data[2],
            is_activated=data[3],
            code_=code
        )

    finally:
        if cursor:
            cursor.close()