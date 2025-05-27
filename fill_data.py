import sqlite3
import os
import dotenv

dotenv.load_dotenv()


conn = sqlite3.connect(os.environ['DATABASE'])
cursor = conn.cursor()


cursor.execute(f"""
    INSERT INTO EduGroup (edu_form, course, edu_group_name) VALUES (1, 1, "БПИ-24");
""")
cursor.execute(f"""
        INSERT INTO EduGroup (edu_form, course, edu_group_name) VALUES (1, 1, "БТМО-24");
    """)
cursor.execute(f"""
        INSERT INTO EduGroup (edu_form, course, edu_group_name) VALUES (1, 1, "БЭЭ-24");
    """)

cursor.execute(f"""
    INSERT INTO EduGroup (edu_form, course, edu_group_name) VALUES (1, 1, "БХТ-24");
""")

cursor.execute(f"""
    INSERT INTO EduGroup (edu_form, course, edu_group_name) VALUES (1, 1, "БМТ-24");
""")


cursor.execute(f"""
    INSERT INTO EduGroup (edu_form, course, edu_group_name) VALUES (1, 3, "БМТ-22");
""")

cursor.execute(f"""
    INSERT INTO EduGroup (edu_form, course, edu_group_name) VALUES (1, 3, "БХТ-22");
""")


cursor.execute(f"""
    INSERT INTO EduGroup (edu_form, course, edu_group_name) VALUES (1, 3, "БПИ-22");
""")
cursor.execute(f"""
        INSERT INTO EduGroup (edu_form, course, edu_group_name) VALUES (1, 3, "БТМО-22");
    """)
cursor.execute(f"""
        INSERT INTO EduGroup (edu_form, course, edu_group_name) VALUES (1, 3, "БЭЭ-22");
    """)


cursor.execute(f"""
    INSERT INTO EduGroup (edu_form, course, edu_group_name) VALUES (1, 2, "БТМО-23");
""")

cursor.execute(f"""
    INSERT INTO EduGroup (edu_form, course, edu_group_name) VALUES (1, 2, "БПИ-23");
""")


cursor.execute(f"""
    INSERT INTO EduGroup (edu_form, course, edu_group_name) VALUES (1, 2, "БХТ-23");
""")

cursor.execute(f"""
    INSERT INTO EduGroup (edu_form, course, edu_group_name) VALUES (1, 2, "БМТ-23");
""")

cursor.execute(f"""
    INSERT INTO EduGroup (edu_form, course, edu_group_name) VALUES (1, 2, "БЭЭ-23");
""")


conn.commit()
conn.close()