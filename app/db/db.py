import sqlite3
from sqlite3 import Cursor
import uuid

from models import model
from forms import GroupForm, MessageForm


def get_user_by_username(db_con: sqlite3.Connection, username: str) -> model.User | None:
    cursor = db_con.cursor()

    try:
        query = """
                   SELECT * FROM Users WHERE username = ?;
               """
        cursor.execute(query, (username,))
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


def has_chat_id(db_con: sqlite3.Connection, tg_chat_id: int) -> model.TelegramGroup:
    cursor = db_con.cursor()

    try:
        query = """
                   SELECT * FROM TgGroup WHERE tg_chat_id = ?;
               """
        cursor.execute(query, (tg_chat_id,))
        data = cursor.fetchone()
        if not data:
            return None
        return model.TelegramGroup(
            chat_id=data[0],
            tg_group_name=data[1],
            is_notify=data[2],
            is_activated=data[3],
            code_=""

        )

    finally:
        if cursor:
            cursor.close()


def _add_relation_tg_edu(cursor: Cursor, tg_group_id: int, edu_group_id: int):
    cursor.execute("""
                       INSERT INTO TgEdu (tg_group_id, edu_id) VALUES (?, ?);
                   """, (tg_group_id, edu_group_id))


def save_tg_group(db_con: sqlite3.Connection, group_form: GroupForm):
    cursor = db_con.cursor()

    try:
        cursor.execute("""
                   INSERT INTO TgGroup (tg_chat_id, tg_group_name, is_notify) VALUES (?, ?, ?);
               """, (group_form.chat_id, group_form.group_name, group_form.is_notify))
        db_con.commit()
        group_id = cursor.lastrowid

        # Добавление Code
        code = str(uuid.uuid4())
        cursor.execute("""INSERT INTO Code (code) VALUES (?);""", (code, ))

        db_con.commit()
        code_id = cursor.lastrowid

        cursor.execute("""
            UPDATE 
                TgGroup
            SET
                code_id = ?
            WHERE
                tg_chat_id = ?
        """, (code_id, group_id))



        # Добавление связей TgEdu

        for edu_group_id in group_form.list_id_edu_group:
            _add_relation_tg_edu(
                cursor,
                tg_group_id=group_id,
                edu_group_id=edu_group_id
            )

    finally:
        if cursor:
            cursor.close()


def get_edu_groups(db_con: sqlite3.Connection) -> list[model.EduGroup]:
    cursor = db_con.cursor()

    try:

        cursor.execute("SELECT * FROM EduGroup;", )

        groups = []
        for _id, course, edu_form, edu_group_name in cursor.fetchall():
            groups.append(
                model.EduGroup(
                    id=_id,
                    course=course,
                    edu_form=edu_form,
                    edu_group_name=edu_group_name
                )
            )

        return groups

    finally:
        if cursor:
            cursor.close()


def get_tg_groups(db_con: sqlite3.Connection) -> list[model.TelegramGroup]:
    cursor = db_con.cursor()

    try:

        cursor.execute("""
        
            SELECT 
                TgGroup.tg_chat_id,
                TgGroup.tg_group_name,
                TgGroup.is_notify,
                TgGroup.is_activated,
                Code.code
            FROM 
                TgGroup
            LEFT JOIN 
                Code
            ON TgGroup.code_id = Code.id;
        """, )

        groups = []
        for chat_id, tg_group_name, is_notify, is_activated, code_ in cursor.fetchall():
            groups.append(
                model.TelegramGroup(
                    chat_id=chat_id,
                    tg_group_name=tg_group_name,
                    is_notify=is_notify,
                    is_activated=is_activated,
                    code_=code_
                )
            )

        return groups

    finally:
        if cursor:
            cursor.close()


def get_govno(db_con: sqlite3.Connection, tg_chat_id: int, edu_id: int):
    cursor = db_con.cursor()

    try:

        cursor.execute("""
            SELECT 
                EduGroup.course,
                EduGroup.edu_form,
                EduGroup.edu_group_name
            FROM 
                TgEdu
            JOIN 
                EduGroup 
            ON 
                TgEdu.edu_id = EduGroup.id
            WHERE 
                TgEdu.tg_group_id = ? 
            AND 
                EduGroup.id = ?;

        """, (tg_chat_id, edu_id))
        data = cursor.fetchone()
        if not data:
            return None
        return data

    finally:
        if cursor:
            cursor.close()


def save_message(db_con: sqlite3.Connection, message_form: MessageForm):
    cursor = db_con.cursor()

    try:

        if message_form.is_send:
            q, args = """
                INSERT INTO Message (text, is_send, date_send) VALUES (?, ?, CURRENT_TIMESTAMP);
            """, (message_form.text, message_form.is_send)
        else:
            q, args = """
               INSERT INTO Message (text) VALUES (?);
           """, (message_form.text, )
        cursor.execute(q, args)

    finally:
        if cursor:
            cursor.close()
