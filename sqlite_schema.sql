CREATE TABLE Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    isActive BOOLEAN DEFAULT TRUE
);

CREATE TABLE Code (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE
);


CREATE TABLE EduGroup (
-- Заранее добавим учебные группы, чтобы группы тг к ним привязать
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    --    Номер курса 1, 2, 3, 4
    course INTEGER NOT NULL,
    --    форма обучения Очная, заочная, очно-заочная
    edu_form INTEGER NOT NULL,
    -- Имя группы БПИ-24 и тд
    edu_group_name TEXT NOT NULL UNIQUE

);

CREATE TABLE TgGroup (
    tg_chat_id INTEGER PRIMARY KEY,
    tg_group_name TEXT NOT NULL,
    is_notify BOOLEAN DEFAULT TRUE,
    is_activated BOOLEAN DEFAULT FALSE,
    data_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    code_id INTEGER,
    FOREIGN KEY (code_id) REFERENCES Code(id)
);


CREATE TABLE TgEdu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    edu_id INTEGER NOT NULL,
    tg_group_id INTEGER NOT NULL,

    FOREIGN KEY (edu_id) REFERENCES EduGroup(id),
    FOREIGN KEY (tg_group_id) REFERENCES TgGroup(tg_chat_id)
);




CREATE TABLE Message (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    is_send BOOLEAN DEFAULT FALSE,
    error_send_flag BOOLEAN DEFAULT FALSE,
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_send TIMESTAMP

);





