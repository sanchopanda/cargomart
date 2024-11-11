import logging
from datetime import datetime

def parse_transport_summary(transport_summary):
    """Извлекает тип кузова и тип погрузки из TransportSummary."""
    if transport_summary == "Не указано":
        logging.warning("TransportSummary не указано.")
        return "Не указано", "Не указано"

    # Извлечение данных из TransportSummary
    cargo_type_start = transport_summary.find("Тип кузова:") + len("Тип кузова:")
    cargo_type_end = transport_summary.find("\n", cargo_type_start)
    cargo_type = transport_summary[cargo_type_start:cargo_type_end].strip()

    loading_type_start = transport_summary.find("Тип погрузки/выгрузки:") + len("Тип погрузки/выгрузки:")
    loading_type_end = transport_summary.find("\n", loading_type_start)
    loading_type = transport_summary[loading_type_start:loading_type_end].strip()

    return cargo_type, loading_type

from datetime import datetime
import logging

def convert_date(date_str):
    """Преобразует дату из различных форматов в 'yyyy-mm-dd'."""
    date_formats = ['%d.%m.%Y', '%Y-%m-%d']  # Список поддерживаемых форматов
    for date_format in date_formats:
        try:
            date_obj = datetime.strptime(date_str, date_format)
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            continue
    logging.warning(f"Некорректный формат даты: {date_str}")
    return None
