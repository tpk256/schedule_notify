CREATE TABLE Courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number INTEGER
);



CREATE TABLE Schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER,
    parity INTEGER,
    hash_excel TEXT,
    url TEXT,
    files_id TEXT,
    count_updates INTEGER,
    date_updated TIMESTAMP,
    date_created TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES Courses(id)
);


CREATE TABLE Subscribers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tg_chat_id INTEGER,
    course_id INTEGER,
    is_deleted INTEGER DEFAULT 0,
    FOREIGN KEY (course_id) REFERENCES Courses(id)
);

