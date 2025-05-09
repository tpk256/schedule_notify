import sqlite3
import os

import dotenv

dotenv.load_dotenv()


conn = sqlite3.connect(os.environ['DATABASE'])
cursor = conn.cursor()
#
# import sqlite3
# conn = sqlite3.connect("/db/schedule_notifier.db")
# cursor = conn.cursor()
#
#
# cursor.execute("""
#     INSERT INTO Users (email, username, password_hash) VALUES (?, ?, ?);
# """,
#                ("tpk256@mail.ru", 'tpk256', "$2b$12$NOMy/HtIi4jPd8oRut/0GOFuSl.9BOLyG4cdc0wCJLrbSE67uY3q.")
#                )
# conn.commit()
# conn.close()
#

for i in range(1, 4 + 1):
    cursor.execute(f"""
        INSERT INTO FileType (id, forma_obucheniya, kurs) VALUES (1{i}, "ochnaya", {i});
    """)

for i in range(1, 4 + 1):
    cursor.execute(f"""
        INSERT INTO FileType (id, forma_obucheniya, kurs) VALUES (2{i}, "zaochnaya", {i});
    """)

for i in range(1, 4 + 1):
    cursor.execute(f"""
        INSERT INTO FileType (id, forma_obucheniya, kurs) VALUES (3{i}, "och-zaoch", {i});
    """)

conn.commit()
conn.close()