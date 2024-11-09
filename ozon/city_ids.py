import logging
import requests
import json
import os

TOKEN_ATI = os.getenv("TOKEN_ATI")

# Функция для получения CityId и отформатированного адреса для массива WayPoints
def get_city_ids(addresses):
    url = "https://api.ati.su/v1.0/dictionaries/locations/parse"
    headers = {
        "Authorization": f"Bearer {TOKEN_ATI}",
        "Content-Type": "application/json"
    }
    # Удаление дубликатов адресов
    unique_addresses = list(set(addresses))
    logging.info(f"Уникальные адреса перед отправкой запроса: {unique_addresses}")

    # Преобразуем в JSON-строку и логируем тело запроса
    payload = json.dumps(unique_addresses)
    logging.info(f"Тело запроса JSON: {payload}")

    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        response_data = response.json()
        logging.info(f"Успешный ответ: {json.dumps(response_data, ensure_ascii=False, indent=4)}")
        return response_data
    else:
        # Логирование кода ошибки и текста ответа для отладки
        logging.error(f"Ошибка запроса: {response.status_code} - {response.text}")
        return {}
