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
        base_url = 'https://cargomart.ru/api/v2/order?filter%5Bavailable%5D=true&filter%5BorderType%5D%5B%5D=auction&filter%5BorderType%5D%5B%5D=express&filter%5Bkind%5D%5B%5D=project&filter%5Bkind%5D%5B%5D=ftl&filter%5Bkind%5D%5B%5D=offer&filter%5Bkind%5D%5B%5D=expeditor-carrier&filter%5Btype%5D=active&filter%5Bbelong%5D=all&filter%5BisGeneralPartner%5D=true&page=1&perPage=60&with%5B%5D=proxy&with%5B%5D=truck-driver'
        # base_url = 'https://cargomart.ru/api/v2/order'

        all_new_orders = {}  # Словарь для хранения новых заявок

        # Начальная пагинация
        page = 1
        while True:
            # Add a 30-second pause at the beginning of each loop iteration
            await asyncio.sleep(30)
            # Выполнение GET-запроса с добавлением куки в заголовки
            print(f"Processing page {page} and order-length {len(all_new_orders)}")
            response = requests.get(base_url, cookies=cookies, params={'page': page})

            # Проверка статуса и вывод ответа
            if response.status_code == 200:
                data = response.json().get('data', {})
                orders = data.get('order', [])
                # полностью парсим только новые заявки
                new_orders = [order for order in orders if f"https://cargomart.ru/orders/active?modal=order-view%3Fhash%3D{order['id']}" not in self.orders]
                processed_orders = await process_orders(new_orders)  # Используем await для вызова асинхронной функции

                # Для старых просто обновляем цену
                for order in orders:
                    order_id = f"https://cargomart.ru/orders/active?modal=order-view%3Fhash%3D{order['id']}"
                    if order_id in self.orders:
                        # Update the rate_with_vat in the existing order
                        current_price = order.get("currentPrice")
                        if current_price is None:
                            print(f"Warning: 'currentPrice' not found for order {order['id']}")
                            continue

                        if isinstance(current_price, str):
                            try:
                                current_price = float(current_price.replace(',', '.'))
                            except ValueError:
                                print(f"Error: Unable to convert currentPrice '{current_price}' to float for order {order['id']}")
                                continue
        
                        self.orders[order_id]['payment']['rate_with_vat'] =  int(round(current_price * 0.85, -2))
                        self.orders[order_id]['payment']['rate_without_vat'] =  int(round(current_price * 0.85 / 1.2, -2))
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