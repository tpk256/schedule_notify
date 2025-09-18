import sqlite3
import os
import json
from typing import Optional

from models import Schedule, Subscribe


class DbConnection:
    # TODO переделать на курсоры, ибо конекшины ДОРОГО
    def __enter__(self):
        self.db_conn = sqlite3.connect(os.environ['DB_NAME'])
        return self.db_conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db_conn.commit()
        self.db_conn.close()


def create_subscribe(tg_chat_id: int, number_course: int, cur: sqlite3.Cursor):
    sql = """
            INSERT INTO
                Subscribers(tg_chat_id, course_id)
            VALUES 
                (?, ?);
        """
    cur.execute(
        sql,
        (tg_chat_id, number_course)
    )


def get_subscribe(tg_chat_id: int, cur: sqlite3.Cursor) -> Optional[Subscribe]:
    sql = """
            SELECT
                *
            FROM
                Subscribers
            WHERE
                tg_chat_id = ? AND is_deleted = 0
            LIMIT 1;
        """
    cur.execute(sql, (tg_chat_id, ))


    result = cur.fetchone()

    if not result:
        return None

    return Subscribe(
        id=result[0],
        tg_chat_id=result[1],
        course_id=result[2]
    )


def delete_subscribe(row_id: int, tg_chat_id: int, cur: sqlite3.Cursor):
    sql = """
            UPDATE
                Subscribers
            SET
                is_deleted = 1
            WHERE
                tg_chat_id = ? AND id = ?;
    """
    cur.execute(sql, (tg_chat_id, row_id))


def get_schedule_info(course: int, parity: int, cur: sqlite3.Cursor) -> Optional[Schedule]:
    sql = """
        SELECT
            *
        FROM
            Schedule
        WHERE
            course_id = ? AND parity = ?
        ORDER BY date_updated DESC
        LIMIT 1;

    """

    cur.execute(
        sql,
        (course, parity)
    )

    founded = cur.fetchone()
    if not founded:
        return None

    return Schedule(
        id=founded[0],

        course_id=founded[1],
        parity=founded[2],
        hash_excel=founded[3],
        url=founded[4],
        files_id=json.loads(founded[5]),

        count_updates=founded[6],
        date_updated=founded[7],
        date_created=founded[8],
    )


