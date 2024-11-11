import requests
import json
import logging
import os
from .config import ATI_API_URL
from dotenv import load_dotenv

load_dotenv()

def fetch_city_ids(unique_loading_addresses, unique_unloading_addresses, authorization_token=os.getenv("AUTHORIZATION_TOKEN")):
    """
    Получает CityID и Street для списка адресов через ATI API.

    Args:
        unique_loading_addresses (set): Множество уникальных адресов для погрузки.
        unique_unloading_addresses (set): Множество уникальных адресов для выгрузки.
        authorization_token (str): Токен авторизации для API.

    Returns:
        Dict[str, Dict[str, Any]]: Словарь, где ключ - исходный адрес, значение - словарь с 'city_id' и 'street' или "Не указано".
    """
    headers = {
        "Authorization": f"Bearer {authorization_token}",
        "Content-Type": "application/json"
    }

    # Объединяем загружаемые и выгружаемые адреса, убирая дубликаты
    all_unique_addresses = unique_loading_addresses.union(unique_unloading_addresses)
    body = list(all_unique_addresses)

    try:
        response = requests.post(ATI_API_URL, headers=headers, data=json.dumps(body), timeout=15)
        if response.status_code == 200:
            data = response.json()

            city_info_mapping = {}
            for address in body:
                address_info = data.get(address, {})
                if address_info.get('is_success'):
                    city_id = address_info.get('city_id', "Не указано")
                    street = address_info.get('street') if address_info.get('street') else None
                    city_info_mapping[address] = {
                        "city_id": city_id,
                        "street": street
                    }
                else:
                    city_info_mapping[address] = {
                        "city_id": "Не указано",
                        "street": None
                    }
            return city_info_mapping
        else:
            logging.error(f"Ошибка при запросе к ATI API: {response.status_code} - {response.text}")
            return {address: {"city_id": "Не указано", "street": None} for address in body}
    except requests.RequestException as e:
        logging.error(f"Исключение при запросе к ATI API: {e}")
        return {address: {"city_id": "Не указано", "street": None} for address in body}