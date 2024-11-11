import logging
from .transport_parser import convert_date

def parse_route(route):
    """Парсит маршрут и возвращает список waypoints."""
    if route == "Не указано":
        logging.warning("Route не указано.")
        return []

    waypoints = []
    route_lines = route.split('●')
    for line in route_lines[1:]:  # Пропускаем первую часть до первого '●'
        line = line.strip()
        if not line:
            continue
        try:
            # Разделяем на тип и остальную часть
            type_part, rest = line.split(':', 1)
            # Извлекаем время и адрес
            time_part, address_part = rest.split('\n', 1)
            # Извлекаем время
            time = time_part.strip()
            # Извлекаем адрес после 'Адрес:'
            if 'Адрес:' in address_part:
                full_address = address_part.split(':', 1)[1].strip()
                # Обрезаем всё после переноса строки
                address = full_address.split('\n')[0].strip()
            else:
                address = 'Не указано'

            # Разделяем время на начало и конец
            if ' - ' in time:
                time_start, time_end = time.split(' - ', 1)
                time_start = time_start.strip()
                time_end = time_end.strip()
            else:
                time_start = time.strip()
                time_end = None  # Отсутствует время окончания

            # Извлекаем дату и преобразуем формат
            if ' ' in time_start:
                date_str, start_time = time_start.split(' ', 1)
                formatted_date = convert_date(date_str)
                loading_time = start_time.strip()
            else:
                formatted_date = None
                loading_time = time_start.strip()

            waypoint_type = 'loading' if 'Погрузка' in type_part else 'unloading' if 'Выгрузка' in type_part else 'unknown'

            # Добавляем в список waypoints
            waypoints.append({
                'type': waypoint_type,
                'date': formatted_date,
                'time_start': loading_time,
                'time_end': time_end,
                'address': address
            })
        except ValueError:
            # Если формат строки некорректен, пропускаем
            logging.warning(f"Некорректный формат строки маршрута: {line}")
            continue

    return waypoints