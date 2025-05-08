import sqlite3

conn = sqlite3.connect("/db/schedule_notifier.db")
cursor = conn.cursor()


with open("sqlite_schema.sql", "r", encoding="utf-8") as file:
    sql_script = file.read()

cursor.executescript(sql_script)
conn.commit()

conn.close()
