import sqlite3
import os

import dotenv


dotenv.load_dotenv()


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.Connection(os.environ['DATABASE'], check_same_thread=False)

    try:
        yield conn

    finally:
        conn.commit()
        conn.close()