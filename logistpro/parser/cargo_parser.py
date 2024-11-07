import re
import logging

def parse_cargo_parameters(cargo_parameters):
    """Парсит параметры груза и возвращает вес и объем."""
    if cargo_parameters == "Не указано":
        logging.warning("CargoParameters не указаны.")
        return "Не указано", "Не указано"

    # Регулярное выражение для извлечения веса и объема
    pattern = r"\)\s*(\d+[.,]?\d*)\s*т\.?\s*(\d+[.,]?\d*)\s*м³|^(\d+[.,]?\d*)\s*т\.?\s*(\d+[.,]?\d*)\s*м³$"
    match = re.search(pattern, cargo_parameters)
    if match:
        if match.group(1) and match.group(2):
            # Совпадение с форматом с скобками
            cargo_weight = match.group(1).replace(',', '.').strip()
            cargo_value = match.group(2).replace(',', '.').strip()
        elif match.group(3) and match.group(4):
            # Совпадение с форматом без скобок
            cargo_weight = match.group(3).replace(',', '.').strip()
            cargo_value = match.group(4).replace(',', '.').strip()
        else:
            cargo_weight = "Не указано"
            cargo_value = "Не указано"
            logging.warning(f"Непредвиденный формат CargoParameters: {cargo_parameters}")
    else:
        # Альтернативный парсинг, если регулярное выражение не сработало
        cargo_parts = cargo_parameters.split(' ')
        if len(cargo_parts) >= 4:
            # Ожидаем формат: "21 т. 86 м³"
            if cargo_parts[1].startswith('т.') and cargo_parts[3].startswith('м³'):
                cargo_weight = cargo_parts[0].replace(',', '.').strip()
                cargo_value = cargo_parts[2].replace(',', '.').strip()
            else:
                cargo_weight = "Не указано"
                cargo_value = "Не указано"
                logging.warning(f"Некорректный формат CargoParameters: {cargo_parameters}")
        else:
            cargo_weight = "Не указано"
            cargo_value = "Не указано"
            logging.warning(f"Некорректный формат CargoParameters: {cargo_parameters}")

    return cargo_weight, cargo_value