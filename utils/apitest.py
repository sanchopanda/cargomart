import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

# Параметры для API
api_url = "https://api.ati.su/v2/cargos/"
authorization_token = os.getenv('ATI_TOKEN')
headers = {
    "Authorization": f"Bearer {authorization_token}",
    "Content-Type": "application/json"
}

# Функция для получения CityId
def get_city_id(loading, unloading, authorization_token):
    api_url = "https://api.ati.su/v1.0/dictionaries/locations/parse"
    headers = {
        "Authorization": f"Bearer {authorization_token}",
        "Content-Type": "application/json"
    }

    # Формируем тело запроса
    body = [loading, unloading]

    response = requests.post(api_url, headers=headers, data=json.dumps(body), timeout=15)

    if response.status_code == 200:
        # Извлечение значений
        data = response.json()  # Преобразуем текст ответа в JSON
        # Извлечение значений
        values = list(data.values())
        print(values)

        # Проверяем, что данные корректны
        if data and len(values) >= 2:
            loading_info = values[0]
            unloading_info = values[1]

            loading_city_id = loading_info.get("city_id") if loading_info.get("is_success") else None
            unloading_city_id = unloading_info.get("city_id") if unloading_info.get("is_success") else None

            return loading_city_id, unloading_city_id
        else:
            print("Некорректные данные от API")
            return None, None
    else:
        print(f"Ошибка при получении ID городов: {response.status_code}")
        return None, None

# Функция для отправки заявки через API
def create_application(params):
    order_id = params.get('order_id')
    loading = params.get('loading')
    unloading = params.get('unloading')
    cargo_type = params.get('cargo_type')
    weight = params.get('weight')
    volume = params.get('volume')
    bet = params.get('bet')
    formatted_date_loading = params.get('formatted_date_loading')
    time_start_loading = params.get('time_start_loading')
    time_end_loading = params.get('time_end_loading')
    formatted_date_unloading = params.get('formatted_date_unloading')
    time_start_unloading = params.get('time_start_unloading')
    time_end_unloading = params.get('time_end_unloading')
    
    loading_city_id, unloading_city_id = get_city_id(loading, unloading, authorization_token)
    if loading_city_id is None or unloading_city_id is None:
        print("Ошибка получения city_id для погрузки или выгрузки")
        return

    # Объявление payload должно быть здесь, вне условия
    payload = {
        "cargo_application": {
            "external_id": order_id,
            "route": {
                "loading": {
                    "city_id": loading_city_id,
                    "address": loading,
                    "location": {
                        "type": "manual",
                        "city_id": loading_city_id,
                        "address": loading
                    },
                    "dates": {
                        "type": "ready",
                        "time": {
                                "type": "bounded",
                                "start": time_start_loading,
                                "end": time_end_loading
                            },
                        "first_date": formatted_date_loading
                    },
                    "cargos": [
                        {
                            "id": 1230099,
                            "name": cargo_type,
                            "weight": {
                                "type": "tons",
                                "quantity": weight
                            },
                            "volume": {
                                "quantity": volume
                            }
                        }
                    ]
                },
                "unloading": {
                    "city_id": unloading_city_id,
                    "address": unloading,
                    "location": {
                        "type": "manual",
                        "city_id": unloading_city_id,
                        "address": unloading
                    },
                    "dates": {
                        "type": "ready",
                         "time": {
                                "type": "bounded",
                                "start": time_start_unloading,
                                "end": time_end_unloading
                            },
                        "first_date": formatted_date_unloading
                    }
                },
                "is_round_trip": False
            },
            "truck": {
                "trucks_count": 1,
                "load_type": "ftl",
                "body_types": [100],
                "body_loading": {
                    "types": [1],
                    "is_all_required": True
                },
                "body_unloading": {
                    "types": [1],
                    "is_all_required": True
                },
                "documents": {
                    "tir": True,
                    "cmr": True,
                    "t1": False,
                    "medical_card": False
                },
                "requirements": {
                    "logging_truck": False,
                    "road_train": False,
                    "air_suspension": True
                },
                "adr": 3,
                "belts_count": 4,
                "is_tracking": True,
                "required_capacity": 15
            },
            "payment": {
                "cash": bet,
                "type": "without-bargaining",
                "currency_type": 1,
                "hide_counter_offers": True,
                "direct_offer": False,
                "prepayment": {
                    "percent": 50,
                    "using_fuel": True
                },
                "payment_mode": {
                    "type": "delayed-payment",
                    "payment_delay_days": 7
                },
                "accept_bids_with_vat": True,
                "accept_bids_without_vat": False,
                "vat_percents": 20,
                "start_rate": 100000,
                "auction_currency_type": 1,
                "bid_step": 10,
                "auction_duration": {
                    "fixed_duration": "1h",
                    "end_time": "2024-09-21T12:00:00.000Z"
                },
                "accept_counter_offers": True,
                "auto_renew": {
                    "enabled": True,
                    "renew_interval": 24
                },
                "is_antisniper": False,
                "rate_rise": {
                    "interval": 1,
                    "rise_amount": 5
                },
                "winner_criteria": "best-rate",
                "time_to_provide_documents": {
                    "hours": 48
                },
                "winner_reselection_count": 2,
                "auction_restart": {
                    "enabled": True,
                    "restart_interval": 24
                },
                "no_winner_end_options": {
                    "type": "archive"
                },
                "rates": {
                    "cash": bet,
                    "rate_with_nds": bet,
                    "rate_without_nds": bet
                }
            },
            "boards": [
                {
                    "id": os.getenv('BOARD_ID'),
                    "publication_mode": "now",
                    "cancel_publish_on_auction_bet": False,
                    "reservation_enabled": True
                }
            ],
            "note": f"{order_id}",
            "contacts": [0]
        }
    }

    # Здесь уже использование payload
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        print(f"Статус ответа: {response.status_code}")
        print(f"Тело ответа: {response.text}")
        print(f"loading_city_id: {loading_city_id}, unloading_city_id: {unloading_city_id}")
        print(f"Параметры заявки: {json.dumps(payload, indent=2)}")

        if response.status_code == 200:
            print("Заявка успешно создана!")
        else:
            print(f"Ошибка при создании заявки: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Ошибка при отправке запроса: {e}")