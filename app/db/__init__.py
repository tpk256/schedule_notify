import sqlite3
import uuid

from models import model
from forms import forms


def get_all_file_type(db_con: sqlite3.Connection) -> list[model.FileType]:
    cursor = db_con.cursor()

    try:
        query = f"""
                   SELECT * FROM FileType;
               """
        cursor.execute(query)
        res = []
        for _id, forma, kurs in cursor.fetchall():
            res.append(
                model.FileType(
                    id=_id,
                    forma_obucheniya=forma,
                    kurs=kurs
                )
            )
        return res

    finally:
        if cursor:
            cursor.close()


def get_user_by_username(db_con: sqlite3.Connection, username: str) -> model.User | None:
    cursor = db_con.cursor()

    try:
        query = """
                   SELECT * FROM Users WHERE username = ?;
               """
        cursor.execute(query, (username, ))
        data = cursor.fetchone()
        if not data:
            return None

        user = model.User(
            id=data[0],
            email=data[1],
            username=data[2],
            hashed_password=data[3],
            isActive=data[4]
        )
        return user

    finally:
        if cursor:
            cursor.close()


def save_tg_group(db_conn: sqlite3.Connection, group: forms.GroupForm):
    cursor = db_conn.cursor()

    try:
        query = """
            INSERT INTO TgGroup (chat_id, name_group, isNotify, ref_file_type) VALUES (?, ?, ?, ?);
        """
        cursor.execute(
            query,
            (
                group.chat_id,
                group.name_group,
                group.is_notify,
                model.FileType.get_file_type(group.forma_obychenia, group.kyrs)
            )
        )

        query = """
                    INSERT INTO Activator (code) VALUES (?);
                """
        cursor.execute(
            query,
            (
                str(uuid.uuid4()),
            )
        )
        db_conn.commit()
        row_activator_id = cursor.lastrowid

        query = """
                    UPDATE 
                        TgGroup 
                    SET 
                        ref_activator = ?
                    WHERE 
                        chat_id = ?;
                """
        cursor.execute(
            query,
            (
                row_activator_id, group.chat_id
            )
        )
    finally:
        if cursor:
            cursor.close()


def has_chat_id(db_conn: sqlite3.Connection, chat_id: str) -> bool:
    cursor = db_conn.cursor()

    try:
        query = """
                SELECT * FROM TgGroup WHERE chat_id = ?;
            """
        cursor.execute(query, (chat_id,))
        if cursor.fetchone():
            return True
        return False

    finally:
        if cursor:
            cursor.close()


def get_groups(db_conn: sqlite3.Connection) -> list[model.Group]:
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
            ORDER BY g.name_group
        """
        cursor.execute(query)
        res = []
        for group in cursor.fetchall():
            res.append(
                model.Group(
                    chat_id=group[0],
                    name_group=group[1],
                    is_notify=group[2],
                    activated=group[3],
                    code=group[4],
                    file_type=group[5]

                )
            )
        return res

    finally:
        if cursor:
            cursor.close()