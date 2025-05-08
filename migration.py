import sqlite3
import os

import dotenv

dotenv.load_dotenv()


conn = sqlite3.connect(os.environ['DATABASE'])
cursor = conn.cursor()


with open("sqlite_schema.sql", "r", encoding="utf-8") as file:
    sql_script = file.read()

cursor.executescript(sql_script)
conn.commit()

conn.close()
