-- Создание таблицы типов файлов
CREATE TABLE FileType (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    forma_obucheniya TEXT NOT NULL,
    kurs INTEGER NOT NULL
);

-- Создание таблицы файлов расписания
CREATE TABLE ScheduleFile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL UNIQUE,
    file_id TEXT NOT NULL,
    hash TEXT NOT NULL UNIQUE,
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_changed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ref_file_type INTEGER NOT NULL,
    FOREIGN KEY (ref_file_type) REFERENCES FileType(id)
);

-- Создание таблицы групп
CREATE TABLE TgGroup (
    chat_id TEXT PRIMARY KEY,
    name_group TEXT NOT NULL,
    isNotify BOOLEAN DEFAULT TRUE,
    ref_file_type INTEGER NOT NULL,
    ref_activator INTEGER NOT NULL,
    FOREIGN KEY (ref_file_type) REFERENCES FileType(id),
    FOREIGN KEY (ref_activator) REFERENCES Activator(id)
);

-- Создание таблицы активации
CREATE TABLE Activator (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    isActivated BOOLEAN DEFAULT 0
);

-- Создание триггера для автоматического обновления даты изменения файла
