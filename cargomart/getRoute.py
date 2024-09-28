
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

authorization_token = os.getenv('ATI_TOKEN')
headers = {
    "Authorization": f"Bearer {authorization_token}",
    "Content-Type": "application/json"
}

# Функция для получения CityId
def get_city_ids(addresses):
    api_url = "https://api.ati.su/v1.0/dictionaries/locations/parse"
    headers = {
        "Authorization": f"Bearer {authorization_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(api_url, headers=headers, data=json.dumps(addresses), timeout=15)

    if response.status_code == 200:
        # Извлечение значений
        data = response.json()  # Преобразуем текст ответа в JSON
        # Извлечение значений
        values = list(data.values())
        print(values)

        # Проверяем, что данные корректны
        if data and len(values) >= 2:
            # Create an array to store city_ids
            city_ids = []
            
            # Iterate through the values and extract city_ids
            for value in values:
                if value.get("is_success"):
                    city_id = value.get("city_id")
                    if city_id is not None:
                        city_ids.append(city_id)
                else:
                    city_ids.append(None)  # Append None for unsuccessful entries
            
         

            return city_ids
        else:
            print("Некорректные данные от API")
            return None, None
    else:
        print(f"Ошибка при получении ID городов: {response.status_code}")
        return None, None

def get_route(data):

    order = data.get('order')

    cargos = [
        {
            'id': 1,
            'name': order['cargoType'],
            'weight': {
                'type': 'tons',
                'quantity': order['cargoWeight']
            },
            'volume': {
                'quantity': order['cargoCapacity']
            }
        }
    ]

    points = []

    
    for point in order['routePoint']:
        
        # Find the corresponding locality for this point
        locality = next((loc for loc in data['locality'] if loc['id'] == point['storage']['code']), None)
        
        processed_point = {
            "type": "loading" if point["type"] == "load" else "unloading",
            "address": point["storage"]["address"] if point["storage"].get("address") else locality["fullName"] if locality else "",
            "location": {
                "type": "manual",
                
                "address": point["storage"]["address"]
            },
            'dates': {
                "type": "from-date" if 'fromDate' in point else "ready",
                "time": {
                    "type": "bounded" if point.get('fromTime') or point.get('toTime') else "round-the-clock",
                    "start": point.get('fromTime', "00:00") if point.get('fromTime') or point.get('toTime') else None,
                    "end": point.get('toTime', "00:00") if point.get('fromTime') or point.get('toTime') else None
                },
                "first_date": point.get('fromDate', None),
                "last_date": point.get('toDate', None)
            }
        }
        points.append(processed_point)
    
    
    # Extract addresses from points
    addresses = [point["address"] for point in points]
    
    # Get city_ids using getCityIds function
    city_ids = get_city_ids(addresses)
    
    # Add city_ids to corresponding points
    for point, city_id in zip(points, city_ids):
        point["city_id"] = city_id 
        point["location"]["city_id"] = city_id

    return {
        "loading": {**points[0], "cargos": cargos},
        "unloading": points[-1],
        "way_points": points[1:-1] if len(points) > 2 else None
    }
