from datetime import datetime


def date_to_str_sqlite(date_time: datetime) -> str:
    return date_time.strftime("%Y-%m-%d %H:%M:%S")


def str_to_date_sqlite(date_time: str) -> datetime:
    return datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")