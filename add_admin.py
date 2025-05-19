
import sqlite3
import os
import dotenv

dotenv.load_dotenv()


conn = sqlite3.connect(os.environ['DATABASE'])
cursor = conn.cursor()


cursor.execute("""
    INSERT INTO Users (email, username, password_hash) VALUES (?, ?, ?);
""",
               ("tpk256@mail.ru", 'tpk256', "$2b$12$NOMy/HtIi4jPd8oRut/0GOFuSl.9BOLyG4cdc0wCJLrbSE67uY3q.")
               )
conn.commit()
conn.close()

