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

        try:
            route = get_route(data)
        except Exception as e:
            print(f"Error in get_route for order {order_data.get('id')}: {str(e)}")
            return None  # Skip this order if there's an error in get_route

        ati_order = {
            "external_id": order_data.get('id'),
            "route": route,
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
                # "rate_without_vat": "?",
                # "cash": "?"
                "rate_with_vat": order["currentPrice"]
            },
            "boards": [
                {
                    "id": os.getenv('BOARD_ID'),
                    "reservation_enabled": True
                }
            ],
            "note": f"https://cargomart.ru/orders/active?modal=order-view%3Fhash%3D{order_data['id']}",
            "contacts": [0]
        }

        return ati_order
    return None


async def process_orders(orders):
    processed_orders = []

    # Обработка заказов
    # for order in orders:
    #     processed_order = await process_order(order)
    #     if processed_order is not None:
    #         processed_orders.append(processed_order)

    processed_order = await process_order(orders[0])
    if processed_order is not None:
        processed_orders.append(processed_order)
           

    return processed_orders


