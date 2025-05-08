import sqlite3
import os

import dotenv

dotenv.load_dotenv()


conn = sqlite3.connect(os.environ['DATABASE'])
cursor = conn.cursor()


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