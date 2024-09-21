import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from utils.config import chrome_driver_path, chrome_options
from cargomart.auth import login
from cargomart.process_order import process_orders
from cargomart.cookies_manager import cookies_file

class Cargomart:
    def get_orders(self):
        # Загрузка куки из файла
        with open(cookies_file, 'r', encoding='utf-8') as file:
            cookies_data = json.load(file)

        # Подготовка куки для запроса
        cookies = {cookie['name']: cookie['value'] for cookie in cookies_data}

        # URL для GET-запроса
        base_url = 'https://cargomart.ru/api/v2/order'
        all_orders = {}  # Словарь для хранения всех заявок

        # Начальная пагинация
        page = 1

        while True:
            # Выполнение GET-запроса с добавлением куки в заголовки
            response = requests.get(base_url, cookies=cookies, params={'page': page})

            # Проверка статуса и вывод ответа
            if response.status_code == 200:
                data = response.json().get('data')
                orders = process_orders(data)
                pagination = data.get('pagination', {})

                # Добавляем текущие заказы в общий словарь
                for order in orders:
                    all_orders[order['id']] = order

                # Проверка, есть ли еще страницы
                total = pagination.get('total', 0)
                per_page = pagination.get('perPage', 0)
                if len(orders) < per_page or total <= len(all_orders):
                    break  # Выходим из цикла, если больше нет страниц
                page += 1  # Переходим к следующей странице
            elif response.status_code == 403:
                print("Ошибка 403: доступ запрещен. Переход к повторной авторизации.")

                service = Service(executable_path=chrome_driver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
                login(self.driver)  # Выполняем авторизацию
                driver.quit()
                with open(cookies_file, 'r', encoding='utf-8') as file:
                    cookies_data = json.load(file)
                cookies = {cookie['name']: cookie['value'] for cookie in cookies_data}
            else:
                print("Ошибка при выполнении запроса:", response.status_code)
                break  # Выход из цикла при ошибке

        return all_orders