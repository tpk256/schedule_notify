import sqlite3
from utils import File, date_to_str_sqlite
from datetime import datetime


def get_hash_by_url(db_conn: sqlite3.Connection, url: str) -> str | None:
    cursor = db_conn.cursor()
    try:
        query = """
            SELECT hash FROM ScheduleFile WHERE url = ?;
        """
        cursor.execute(query, (url, ))
        res = cursor.fetchone()

        if res:
            return res[0]
    finally:
        if cursor:
            cursor.close()

    return None


def save_schedule_file(db_con: sqlite3.Connection, file: File):
    cursor = db_con.cursor()
    try:
        query = """
                INSERT INTO ScheduleFile (url, file_id, hash, ref_file_type) VALUES (?, ?, ?, ?);
            """
        cursor.execute(query, (file.link.url, file.file_id, file.hash, file.link.file_type))

    finally:
        if cursor:
            cursor.close()


def update_schedule_file(db_con: sqlite3.Connection, file: File):
    cursor = db_con.cursor()
    date_time = date_to_str_sqlite(datetime.now())
    try:
        query = f"""
                   UPDATE 
                        ScheduleFile
                   SET 
                        hash = ?,
                        file_id = ?,
                        date_changed = ?
                   WHERE url = ?;
               """
        cursor.execute(query, (file.hash, file.file_id, date_time, file.link.url))

    finally:
        if cursor:
            cursor.close()



