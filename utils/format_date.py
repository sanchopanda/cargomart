import datetime

def format_date(date_str):
    # Определяем текущий год
    current_year = datetime.datetime.now().year

    # Словарь для преобразования названий месяцев
    months = {
        "янв": "01", "фев": "02", "мар": "03", "апр": "04",
        "май": "05", "июн": "06", "июл": "07", "авг": "08",
        "сен": "09", "окт": "10", "ноя": "11", "дек": "12"
    }

    try:
        # Разбиваем строку на части (например, '19 сен 03:00–05:00')
        parts = date_str.split()
        if len(parts) < 3:
            raise ValueError("Неверный формат даты. Ожидалось как минимум 3 части.")

        day = parts[0]  # День
        month = months.get(parts[1].lower(), '01')  # Месяц
        time_part = parts[2]  # Время (например, 03:00–05:00)

        # Форматируем дату в формате гггг-мм-дд
        formatted_date = f"{current_year}-{month}-{day}"

        # Проверяем, есть ли диапазон времени
        if '–' in time_part:
            start_time, end_time = time_part.split('–')
        else:
            start_time = time_part
            end_time = None

        # Возвращаем дату и диапазон времени
        return formatted_date, start_time, end_time
    except (IndexError, KeyError, ValueError) as e:
        print(f"Ошибка при обработке даты: {e}")
        return date_str, '00:00', '00:00'  # Если ошибка, возвращаем исходные значения
