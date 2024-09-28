from cargomart.types import truckTypes, loadingTypes, currencyTypes
from cargomart.getRoute import get_route
from cargomart.cookies_manager import cookies_file
import requests
import os
import json
import asyncio

api_url = "https://cargomart.ru/api/v2/order/"

# Чтение куки из файла
with open(cookies_file, 'r', encoding='utf-8') as file:
    cookies_data = json.load(file)

# Подготовка куки для запроса
cookies = {cookie['name']: cookie['value'] for cookie in cookies_data}


async def process_order(order):
    response = requests.get(api_url + str(order['id']), cookies=cookies)
    if response.status_code == 200:
        data = response.json()['data']  # Поправил на .json(), так как это JSON-ответ
        order_data = data.get('order')

        print(order_data.get('id'))

        ati_order = {
            "external_id": order_data.get('id'),
            "route": get_route(data),
            "truck": {
                "load_type": "dont-care",
                "body_types": [truckTypes[order_data["truckTypeId"]]],
                "body_loading": {
                    "types": [loadingTypes[order["loading"][0]]]
                },
                "body_unloading": {
                    "types": [loadingTypes[order["loading"][0]]]
                },
                "temperature": order_data.get("temperature") if "temperature" in order_data else None,
                "documents": {
                    # ToDo: разобраться
                    # tir: boolean (nullable),
                    # cmr: boolean (nullable),
                    # t1: boolean (nullable),
                    "medical_card": order_data.get("condition", {}).get("needHygieneCert", False),
                }
            },
            "payment": {
                "type": "without-bargaining",
                "currency_type": currencyTypes[order["currencyCode"]],
                # ToDo: разобраться тут
                # "cash":
                # "rate_without_nds":
                "rates": {
                    # "cash": ?,
                    # "rate_without_nds": ?,
                    "rate_with_nds": order["currentPrice"]                    
                }           
            },
            "boards": [
                {
                    "id": os.getenv('BOARD_ID'),
                    "reservation_enabled": True
                }
            ],
            "contacts": [0]
        }

        return ati_order
    return None


async def process_orders(response):
    processed_orders = []

    # Обработка заказов
    if response['order']:
        order = response['order'][1]  # Только первый заказ
        processed_order = await process_order(order)
        if processed_order:
            processed_orders.append(processed_order)

    return processed_orders
