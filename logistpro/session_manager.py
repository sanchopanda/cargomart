import os
import requests
import json
import logging
from logistpro.cookie_manager import load_cookies
from logistpro.auth import login_and_save_cookies
from logistpro.config import COOKIE_FILE, DATA_URL, AUTHORIZATION_TOKEN, MAIN_URL

def add_cookies_to_session(session, cookie_file):
    """Загружает куки из файла и добавляет их в сессию.

    Args:
        session (Session): Объект сессии Requests.
        cookie_file (str): Путь к файлу с куками.

    Returns:
        bool: True, если куки успешно загружены и добавлены, иначе False.
    """
    if os.path.exists(cookie_file) and os.path.getsize(cookie_file) > 0:
        try:
            # Загружаем куки из файла
            cookies = load_cookies(cookie_file)
            for cookie in cookies:
                session.cookies.set(cookie['name'], cookie['value'], domain=cookie.get('domain'))
            logging.info("Куки успешно добавлены в сессию.")
            return True
        except Exception as e:
            logging.error(f"Не удалось добавить куки в сессию: {e}")
            return False
    logging.info("Файл с куками отсутствует или пуст.")
    return False

def get_data_with_cookies(cookie_file):
    """Получает данные с использованием кук.

    Returns:
        dict или None: Полученные данные или None в случае ошибки.
    """
    session = requests.Session()

    # Пытаемся загрузить куки и сделать запрос
    if add_cookies_to_session(session, cookie_file):
        logging.info("Отправка запроса с использованием существующих кук.")
        response = session.get(DATA_URL)

        if response.status_code == 200:
            try:
                data = response.json()
                logging.info("Данные успешно получены с API.")
                return data
            except json.JSONDecodeError:
                logging.error("Ошибка парсинга JSON.")
                return None
        elif response.status_code in (403, 401):
            logging.info(f"Получен статус {response.status_code}, требуется авторизация...")
        else:
            logging.error(f"Ошибка: {response.status_code}")
            return None
    else:
        logging.info("Файл с куками отсутствует или пуст.")

    # Если куки не подходят (403 или 401) или их нет, авторизуемся через Selenium
    login_and_save_cookies(cookie_file)
    
    # Повторяем запрос с новыми куками
    if add_cookies_to_session(session, cookie_file):
        logging.info("Отправка запроса после авторизации.")
        response = session.get(DATA_URL)
        if response.status_code == 200:
            try:
                data = response.json()
                logging.info("Данные успешно получены после авторизации.")
                return data
            except json.JSONDecodeError:
                logging.error("Ошибка парсинга JSON после авторизации.")
                return None
        else:
            logging.error(f"Ошибка после авторизации: {response.status_code}")
            return None
    else:
        logging.error("Не удалось загрузить новые куки после авторизации.")
        return None