import sqlite3
import datetime
import json
from typing import Optional

from pydantic import BaseModel

from models import File, Event, Schedule


def get_subscribes_by_course(course_id: int, cur: sqlite3.Cursor) -> list[int]:
    sql = """
            SELECT
                tg_chat_id
            FROM
                Subscribers
            WHERE
                course_id = ? AND is_deleted = 0
        """
    cur.execute(sql, (course_id, ))

    res = []


    for row in cur.fetchall():
        res.append(row[-1])

    return res


def find_schedule_info_by_hash_and_url(hash_excel: str, url: str, cur: sqlite3.Cursor):
    cur.execute("""
        SELECT 
            * 
        FROM 
            Schedule 
        WHERE
            hash_excel = ? AND  url = ?;
    
    """, (hash_excel, url))

    return cur.fetchone()


def find_schedule_info_by_url(url: str, cur: sqlite3.Cursor):
    cur.execute("""
        SELECT 
            * 
        FROM 
            Schedule 
        WHERE
            url = ?;

    """, (url, ))

    return cur.fetchone()



def update_schedule_info(file: File, files_id: list[str], old_schedule: Schedule, cur: sqlite3.Cursor) -> Event:

    sql = """
        UPDATE 
            Schedule
        SET
            hash_excel = ?,
            files_id = ?,
            count_updates = ?,
            date_updated = ?
        WHERE 
            id = ?
    """

    cur.execute(
        sql,
        (
            file.hash,
            json.dumps(files_id),
            old_schedule.count_updates + 1,
            int(datetime.datetime.now().timestamp()),
            old_schedule.id

        )

    )




    return Event(type="update", course=file.link.kyrs, parity=old_schedule.parity)



def save_schedule_info(file: File, files_id: list[str], cur: sqlite3.Cursor) -> Event:

    founded = find_schedule_info_by_url(file.link.url, cur)

    if founded:
        old_schedule = Schedule(
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


        # иначе обновление!
        return update_schedule_info(file, files_id, old_schedule, cur)



    sql = """
        INSERT INTO Schedule(
            course_id, 
            parity, 
            hash_excel, 
            url, 
            files_id, 
            count_updates, 
            date_updated,
            date_created
        ) VALUES(?, ?, ?, ?, ?, ?, ?, ?);
    """

    cur.execute(
        sql,
        (
            file.link.kyrs,
            file.link.parity,
            file.hash,
            file.link.url,
            json.dumps(files_id),
            0,
            int(datetime.datetime.now().timestamp()),
            int(datetime.datetime.now().timestamp())

        )
         )

    return Event(type="save", course=file.link.kyrs, parity=file.link.parity)







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


