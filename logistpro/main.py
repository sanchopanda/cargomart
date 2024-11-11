import os
import json
import logging
import time  # Добавлен импорт модуля time
from dotenv import load_dotenv
from logistpro.config import (
    COOKIE_FILE,
    AUTHORIZATION_TOKEN
)
from logistpro.session_manager import get_data_with_cookies
from logistpro.application_processor import process_applications
from logistpro.auth import login_and_save_cookies  # Импорт функции авторизации


class Logistpro:
    def __init__(self):
        pass

    async def get_orders(self):
        try:
            if not os.path.exists(COOKIE_FILE) or os.path.getsize(COOKIE_FILE) == 0:
                login_and_save_cookies(COOKIE_FILE)

            # Получаем данные с использованием куки
            data = get_data_with_cookies(COOKIE_FILE)

            if data is not None and 'Items' in data:
                request_bodies = process_applications(data, AUTHORIZATION_TOKEN)
                
                return request_bodies
            else:
                logging.info("Нет данных для обработки.")

        except Exception as e:
            logging.exception(f"Произошла ошибка: {e}")
            return {}
