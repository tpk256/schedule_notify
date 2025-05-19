import re
from datetime import datetime
from pprint import pprint

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.utils import get_column_letter
from openpyxl.utils import column_index_from_string, coordinate_to_tuple

from models import model


date_re = re.compile(
    r'\b'                                  # граница слова
    r'(?P<day>0?[1-9]|[12]\d|3[01])'       # день: 1–9 или 01–09, 10–29, 30,31
    r'\.'                                  # точка-разделитель
    r'(?P<month>0?[1-9]|1[0-2])'           # месяц: 1–9 или 01–09, 10–12
    r'\.'                                  # точка-разделитель
    r'(?P<year>\d{4})'                     # год: ровно 4 цифры
    r'\b'                                  # граница слова
)


def parse_date(date_string: str) -> list[datetime]:
    results = []
    for m in date_re.finditer(date_string):
        d = int(m.group('day'))
        m_ = int(m.group('month'))
        y = int(m.group('year'))
        try:
            results.append(datetime(y, m_, d))
        except ValueError:
            continue
    return results


def find_cell_corners(ws, target_value, flag_in=False):
    """
        Ищет в ws (Worksheet) ячейку со значением target_value.
        Если она в составе merged cell, возвращает углы этого диапазона,
        иначе – просто её координату дважды.
        Возвращает кортеж (top_left, bottom_right) как строки вида 'B3'.
    """
    # Сначала находим саму ячейку
    for row in ws.iter_rows():
        for cell in row:
            if target_value in str(cell.value):

                if not flag_in:
                    if target_value != cell.value:
                        continue
                coord = cell.coordinate

                # Проверяем, в какой merged-диапазон она входит
                for merge_range in ws.merged_cells.ranges:

                    if coord in merge_range:  # например 'B3' in 'B3:D5'
                        # bounds = (min_col, min_row, max_col, max_row)
                        min_col, min_row, max_col, max_row = merge_range.bounds
                        top_left = f"{get_column_letter(min_col)}{min_row}"
                        bottom_right = f"{get_column_letter(max_col)}{max_row}"
                        return top_left, bottom_right

                # Если не в merged, то углы – она сама
                return coord, coord

    # Если ничего не найдено
    return None, None


def find_cell_corners_in_region(ws, target_value, top_left: str, bottom_right: str, flag_in: bool = False):
    """
    Ищет в ws (Worksheet) ячейку со значением target_value
    внутри прямоугольника от top_left до bottom_right (включительно).
    Если найдена ячейка вне merged-диапазона — возвращает её координату дважды.
    Если она часть merged-диапазона — возвращает углы этого диапазона.
    :param ws: Worksheet
    :param target_value: искомое значение (строка или число)
    :param top_left: верхняя-левая ячейка области, например "B2"
    :param bottom_right: нижняя-правая ячейка области, например "E10"
    :param flag_in: если True, ищет по вхождению подстроки (target_value in str(cell.value))
                    если False, ищет точное совпадение (cell.value == target_value)
    :return: (top_left_coord, bottom_right_coord) или (None, None), где coords — строки вида "C5"
    """
    min_row, min_col = coordinate_to_tuple(top_left)
    max_row, max_col = coordinate_to_tuple(bottom_right)

    for row in range(min_row, max_row + 1):
        for col in range(min_col, max_col + 1):
            cell = ws.cell(row=row, column=col)
            if cell.value is None:
                continue
            if flag_in:
                if str(target_value) not in str(cell.value):
                    continue
            else:
                if cell.value != target_value:
                    continue

            coord = cell.coordinate
            # Проверяем merged-диапазоны
            for merge_range in ws.merged_cells.ranges:
                if coord in merge_range:
                    min_c, min_r, max_c, max_r = merge_range.bounds
                    tl = f"{get_column_letter(min_c)}{min_r}"
                    br = f"{get_column_letter(max_c)}{max_r}"
                    return tl, br
            # Не в merged — возвращаем саму ячейку
            return coord, coord

    return None, None


def _parse_sub_groups(
        ws: Worksheet,
        start_col: int,
        end_col: int,   # depracated
        row: int,
) -> tuple[model.SubGroup | None, model.SubGroup | None]:
    temp = []
    # print(start_col, end_col, end_col - start_col + 1, row)

    # for i in range(start_col, end_col + 1):
    for i in range(start_col, start_col + 4):
        cell = ws[get_column_letter(i) + str(row)]

        temp.append(cell.value)

    ans = (None, None)

    if temp[0] and temp[1] and temp[2] and temp[3]:
        ans = (
            model.SubGroup(
                number=1,
                subject=temp[0],
                aud=str(temp[1])
            ),
            model.SubGroup(
                number=2,
                subject=temp[2],
                aud=str(temp[3])
            )
        )

    elif temp[0] and temp[3]:
        ans = (
            model.SubGroup(
                number=1,
                subject=temp[0],
                aud=str(temp[3])
            ),
            model.SubGroup(
                number=2,
                subject=temp[0],
                aud=str(temp[3])
            )
        )
    elif temp[0] and temp[1]:
        ans = (
            model.SubGroup(
                number=1,
                subject=temp[0],
                aud=str(temp[1])
            ), None
        )
    elif temp[2] and temp[3]:
        ans = (
            None,
            model.SubGroup(
                number=2,
                subject=temp[2],
                aud=str(temp[3])
            )
        )

    return ans


def get_pair(ws: Worksheet, data: dict, num_pair: int, range: tuple) -> model.Pair | None:

    cell, _ = find_cell_corners_in_region(ws, num_pair, range[0], range[1])
    if not cell:
        return None
    start_pos = data['group_pos'][0][0] + cell[1:]
    end_pos = data['group_pos'][1][0] + cell[1:]

    time_pair = ws[get_column_letter(column_index_from_string(cell[0]) + 1) + cell[1:]]     # Время для текущей пары
    sub_groups = _parse_sub_groups(
        ws,
        column_index_from_string(data['group_pos'][0][0]),
        column_index_from_string(data['group_pos'][1][0]) + data.get('flag_offset_aud', 0),
        int(cell[1:])
    )

    return model.Pair(
        number=num_pair,
        time=time_pair.value,
        sub_groups=sub_groups
    )


def get_day(ws: Worksheet, day_name: str, data, group_pos: tuple[str, str]) -> model.Day | None:
    c1, c2 = find_cell_corners(ws, day_name, flag_in=True)
    if c1[0] != c2[0]:  # Если будний день, то день недели расположен в одном столбце, иначе выходной

        return ws[c1].value

    # print(day_name)
    data["group_pos"] = group_pos


    # Из-за странного расположения аудитории в таблице нужно чекать

    col = get_column_letter(column_index_from_string(group_pos[-1][0]) + 1)
    row = group_pos[0][1:]
    if ws[col + row].value == 'Ауд.' or ws[col + str(int(row) + 1)].value == 'Ауд.':
        data['flag_offset_aud'] = 1

    pairs = []

    for num_pair in range(1, 7 + 1):
        start_pos = data.get("number_pos")[0][0] + c1[1:]
        end_pos = data.get("number_pos")[0][0] + c2[1:]
        pairs.append(
            get_pair(ws, data, num_pair, (start_pos, end_pos))
        )
    #
    # pprint(
    #     (
    #         day_name,
    #         tuple(pairs),
    #         parse_date(ws[c1].value)
    #     )
    # )
    day = model.Day(
        name=day_name,
        pairs=tuple(pairs),
        date=parse_date(ws[c1].value)[-1]
    )
    return day


def _parse_group(ws: Worksheet, name_group, data: dict) -> model.Group:
    name_group_pos = find_cell_corners(ws, name_group)
    data['name_group_pos'] = name_group_pos
    left_top_corner = name_group_pos[0]
    right_bottom_corner = name_group_pos[1][0] + data.get("end_row")
    # print(left_top_corner, right_bottom_corner, "<----", "область группы в таблице")
    days = []
    for day_name in ('Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота'):
        days.append(
            get_day(
                ws,
                day_name,
                data,
                (left_top_corner, right_bottom_corner)
            )
        )

    schedule = model.Schedule(days=tuple(days))
    return model.Group(
        name=name_group,
        schedule=schedule
    )


def _get_name_groups(title_ws: str) -> list[str]:
    return re.findall(r'[^,\s]+', title_ws)


range_re = re.compile(
    r'\b'
    r'(?P<d1>0?[1-9]|[12]\d|3[01])\.'        # день начала
    r'(?P<m1>0?[1-9]|1[0-2])'                # месяц начала
    r'-'                                     
    r'(?P<d2>0?[1-9]|[12]\d|3[01])\.'         # день конца
    r'(?P<m2>0?[1-9]|1[0-2])'                # месяц конца
    r'\.(?P<y>\d{4})'                        # год (4 цифры)
    r'\b'
)


def parse_date_range(text: str) -> tuple[datetime, datetime] | None:
    """
    Ищет в тексте диапазон дат DD.MM-DD.MM.YYYY и возвращает
    кортеж (start_date, end_date) как datetime.date.
    Если не найдено — возвращает None.
    """
    m = range_re.search(text)
    if not m:
        return None

    d1, m1 = int(m.group('d1')), int(m.group('m1'))
    d2, m2 = int(m.group('d2')), int(m.group('m2'))
    y  = int(m.group('y'))

    # Попробуем создать объекты date; если диапазон некорректен, пробросим ошибку
    start = datetime(y, m1, d1)
    end   = datetime(y, m2, d2)
    return start, end


def parse_xlsx(file_name: str) -> [list[model.Group], bool]:
    wb = load_workbook(file_name)
    work_sheets = wb.worksheets[:2]    # В последней таблице находятся данные для подключения Zoom и тд
    groups = []
    flag_parity = bool(find_cell_corners(work_sheets[0], "Нечетная неделя")[0])
    print(flag_parity)
    for i, ws in enumerate(work_sheets, 1):

        names = _get_name_groups(ws.title)
        data = dict()
        data["date_pos"] = find_cell_corners(ws, 'Дата', )
        data["number_pos"] = find_cell_corners(ws, '№')
        data["time_pos"] = find_cell_corners(ws, 'Время')
        data["end_row"] = find_cell_corners(ws, 'Суббота', flag_in=True)[-1][1:]
        for name_group in names:
            groups.append(_parse_group(ws, name_group, data=data))

    return groups, flag_parity

#
# import os
#
# for file in os.listdir():
#     if file.endswith('xlsx'):
#         parse_xlsx(file)
