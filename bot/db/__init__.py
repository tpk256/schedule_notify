import sqlite3
import os

from models import model


def get_group(db_conn: sqlite3.Connection, chat_id: str) -> model.Group:
    cursor = db_conn.cursor()

    try:
        query = """
            SELECT 
                g.chat_id,
                g.name_group,
                g.isNotify,
                g.isActivated,
                a.code,
                g.ref_file_type
            FROM TgGroup AS g
            
            LEFT JOIN Activator AS a
              ON g.ref_activator = a.id
            WHERE 
                g.chat_id = ?
        """
        cursor.execute(query, (chat_id, ))
        group = cursor.fetchone()
        if not group:
            return None

        return model.Group(
                    chat_id=group[0],
                    name_group=group[1],
                    is_notify=group[2],
                    activated=group[3],
                    code=group[4],
                    file_type=group[5]
        )

    finally:
        if cursor:
            cursor.close()


class DbConnection:
    def __enter__(self):
        self.db_conn = sqlite3.connect(os.environ['DATABASE'])
        return self.db_conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db_conn.commit()
        self.db_conn.close()


def activate_group(db_conn: sqlite3.Connection, chat_id: str):
    cursor = db_conn.cursor()

    try:
        query = """
            UPDATE 
                TgGroup
            SET
                isActivated = ?
            WHERE 
                chat_id = ?
        """
        cursor.execute(query, (True, chat_id))

    finally:
        if cursor:
            cursor.close()


def get_file_id_for_group(db_conn: sqlite3.Connection, file_type: int) -> str | None:
    cursor = db_conn.cursor()

    try:
        query = """
            SELECT 
                file_id
            FROM
                ScheduleFile
            WHERE 
                ref_file_type = ?
            ORDER BY date_changed DESC   
            LIMIT 1;
            
        """
        cursor.execute(query, (file_type, ))
        res = cursor.fetchone()
        print(res)
        if res:
            return res[-1]
        return None

    finally:
        if cursor:
            cursor.close()