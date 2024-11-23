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
    counter = 0
    while counter < 3:  # Цикл для повторного запроса в случае ошибки
        try:
            response = requests.get(api_url + str(order['id']), cookies=cookies)
            break  # Успешный запрос, выходим из цикла
        except Exception as e:
            print(f"Ошибка запроса: {e}. Повторная попытка через 5 секунд.")
            await asyncio.sleep(3)  # Ждем перед повтором
            counter = counter + 1
    
    if response and response.status_code == 200:
        data = response.json()['data']  # Поправил на .json(), так как это JSON-ответ
        order_data = data.get('order')

        try:
            route = get_route(data)
        except Exception as e:
            print(f"Error in get_route for order {order_data.get('id')}: {str(e)}")
            return None  # Skip this order if there's an error in get_route

        current_price = order.get("currentPrice")
        if current_price is None:
            print(f"Warning: 'currentPrice' not found for order {order_data.get('id')}")
            return None

        if isinstance(current_price, str):
            try:
                current_price = float(current_price.replace(',', '.'))
            except ValueError:
                print(f"Error: Unable to convert currentPrice '{current_price}' to float for order {order_data.get('id')}")
                return None

        try:
            ati_order = {
                "external_id": f"https://cargomart.ru/orders/active?modal=order-view%3Fhash%3D{order_data.get('id')}",
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
                    "rate_with_vat": int(round(current_price * 0.85, -2)),
                    "rate_without_vat": int(round(current_price * 0.85 / 1.2, -2))
                },
                "boards": [
                    {
                        "id": os.getenv('BOARD_ID'),
                        "reservation_enabled": False
                    }
                ]
            }
        except:
            print(f"Error: Unable to create ati body {order_data.get('id')}")
            return None

        return ati_order
    else:
        error_message = f"Error: Unable to process order {order.get('id')}. Invalid or missing data."
        # error_data = response.json()
        # if 'message' in error_data and error_data['message']:
        #     error_message = error_data['message'][0].get('title', 'Unknown error')
        #     print(f"Error: {error_message}")
          
    return None


async def process_orders(orders):

    processed_orders = []

    for order in orders:
        processed_order = await process_order(order)
        if processed_order is not None:
            processed_orders.append(processed_order)
            

    # processed_order = await process_order(orders[0])
    # if processed_order is not None:
    #     processed_orders.append(processed_order)

    return processed_orders

