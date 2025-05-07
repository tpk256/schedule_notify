import sqlite3

from models import model


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
