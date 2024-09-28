import json
import requests
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from utils.config import chrome_driver_path, chrome_options
from cargomart.auth import login
from cargomart.process_order import process_orders
from cargomart.cookies_manager import cookies_file

class Cargomart:
    def __init__(self):
        self.orders = {}

    async def get_orders(self):
        # Загрузка куки из файла
        with open(cookies_file, 'r', encoding='utf-8') as file:
            cookies_data = json.load(file)

        # Подготовка куки для запроса
        cookies = {cookie['name']: cookie['value'] for cookie in cookies_data}

        # URL для GET-запроса
        base_url = 'https://cargomart.ru/api/v2/order'
        all_new_orders = {}  # Словарь для хранения новых заявок

        # Начальная пагинация
        page = 1

        while True:
            # Выполнение GET-запроса с добавлением куки в заголовки
            response = requests.get(base_url, cookies=cookies, params={'page': page})

            # Проверка статуса и вывод ответа
            if response.status_code == 200:
                data = response.json().get('data', {})
                orders = data.get('order', [])
                # полностью парсим только новые заявки
                new_orders = [order for order in orders if order['id'] not in self.orders]
                processed_orders = await process_orders(new_orders)  # Используем await для вызова асинхронной функции

                # Для старых просто обновляем цену
                for order in orders:
                    order_id = order['id']
                    if order_id in self.orders:
                        # Update the rate_with_vat in the existing order
                        self.orders[order_id]['payment']['rate_with_vat'] = order['currentPrice']
                        processed_orders.append(self.orders[order_id])

                pagination = data.get('pagination', {})

                # Добавляем текущие заказы в общий словарь
                for order in processed_orders:
                    all_new_orders[order['external_id']] = order  # Исправлено на 'external_id'

                # Проверка, есть ли еще страницы
                total = pagination.get('total', 0)
                per_page = pagination.get('perPage', 0)
                if len(orders) < per_page or total <= len(all_new_orders):
                    break  # Выходим из цикла, если больше нет страниц
                page += 1  # Переходим к следующей странице
            elif response.status_code == 403:
                print("Ошибка 403: доступ запрещен. Переход к повторной авторизации.")

                service = Service(executable_path=chrome_driver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
                login(driver)  # Выполняем авторизацию
                driver.quit()
                with open(cookies_file, 'r', encoding='utf-8') as file:
                    cookies_data = json.load(file)
                cookies = {cookie['name']: cookie['value'] for cookie in cookies_data}
            else:
                print("Ошибка при выполнении запроса:", response.status_code)
                break  # Выход из цикла при ошибке

        # обновляем значение self.orders
        self.orders = all_new_orders
        return all_new_orders