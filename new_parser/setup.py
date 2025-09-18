import os
import sqlite3






















if __name__ == '__main__':

    path_pdf = 'pdfs'
    path_excel = 'excels'
    path_jpg = 'jpgs'
    path_database = r'C:\Users\tpk25\PycharmProjects\schedule_notify\new_parser\db_bot.data'

    if os.path.exists(path_pdf):
        if os.path.isfile(path_pdf):
            print(f"{path_pdf} is file!!!")

    else:
        os.mkdir(path_pdf)

    if os.path.exists(path_excel):
        if os.path.isfile(path_excel):
            print(f"{path_excel} is file!!!")
    else:
        os.mkdir(path_excel)

    if os.path.exists(path_jpg):
        if os.path.isfile(path_jpg):
            print(f"{path_jpg} is file!!!")

    else:
        os.mkdir(path_jpg)

    if os.path.exists('sqlite_schema.sql'):
        if not os.path.exists(path_database):

            db_conn = sqlite3.connect(path_database)
            cursor = db_conn.cursor()
            with open('sqlite_schema.sql', mode='r') as schema:
                cursor.executescript(schema.read())
            db_conn.commit()


            for i in range(1, 4 + 1):
                cursor.execute(f"""
                    INSERT INTO Courses (id, number) VALUES({i}, {i});
                """)

            db_conn.commit()



            cursor.close()
            db_conn.close()
        else:
            print("Бд уже есть.")
    else:
        print("Нет схемы sql!")
