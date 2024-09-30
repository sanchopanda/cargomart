
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
def get_city_ids(addresses_from_points, addresses_from_locality):
    api_url = "https://api.ati.su/v1.0/dictionaries/locations/parse"
    headers = {
        "Authorization": f"Bearer {authorization_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(api_url, headers=headers, data=json.dumps(addresses_from_points), timeout=15)

    if response.status_code == 200:
        # Извлечение значений
        data = response.json()  # Преобразуем текст ответа в JSON

        # Проверяем, что данные корректны
        if data:
            # Create an array to store city_ids
            city_ids = []
            
            # Iterate through the data and extract city_ids
            for index, (address, value) in enumerate(data.items()):
                if value.get("is_success"):
                    city_id = value.get("city_id")
                    if city_id is not None:
                        city_ids.append(city_id)
                    else:
                        # Try to get city_id using the address from locality
                        locality_address = addresses_from_locality[index]
                        locality_response = requests.post(api_url, headers=headers, data=json.dumps([locality_address]), timeout=15)
                        if locality_response.status_code == 200:
                            locality_data = locality_response.json()
                            locality_value = locality_data.get(locality_address, {})
                            if locality_value.get("is_success"):
                                locality_city_id = locality_value.get("city_id")
                                if locality_city_id is not None:
                                    city_ids.append(locality_city_id)
                                else:
                                    raise ValueError(f"City ID not found for both addresses: {address} and {locality_address}")
                            else:
                                raise ValueError(f"Failed to get city ID for both addresses: {address} and {locality_address}")
                        else:
                            city_ids.append(None)
                            print(f"Error getting city ID for locality address: {locality_address}")
                else:
                    city_ids.append(None)  # Append None for unsuccessful entries
                    print(f"Failed to get city ID for address: {address}")
         

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

    addresses_from_locality = []
    
    for index, point in enumerate(order['routePoint']):
        
        # Find the corresponding locality for this point
        locality = next((loc for loc in data['locality'] if loc['id'] == point['storage']['code']), None)
        
        processed_point = {
            "type": "loading" if point["type"] == "load" else "unloading",
            "location": {
                "type": "manual",                
                "address": point["storage"]["address"] if point["storage"].get("address") else locality["fullName"] if locality else ""
            },
            'dates': {
                "type": "from-date" if index == 0 else None,
                "time": {
                    "type": "bounded" if point.get('fromTime') or point.get('toTime') else "round-the-clock",
                    "start": point.get('fromTime')[:5] if point.get('fromTime') else None,
                    "end": point.get('toTime')[:5] if point.get('toTime') else None
                },
                "first_date": point.get('fromDate', None),
                "last_date": point.get('toDate',  point.get('fromDate', None))
            }
        }
        points.append(processed_point)

        addresses_from_locality.append(locality["fullName"] if locality else point["storage"].get("address", ""))
        
    
    adresses_from_points = [point["location"]["address"] for point in points]
   
    try:
        city_ids = get_city_ids(adresses_from_points, addresses_from_locality)
    except Exception as e:
        raise Exception(f"Error getting city IDs: {str(e)}")
    
    # Add city_ids to corresponding points
    for point, city_id in zip(points, city_ids):
        point["location"]["city_id"] = city_id

    return {
        "loading": {**points[0], "cargos": cargos},
        "unloading": points[-1],
        "way_points": points[1:-1] if len(points) > 2 else None
    }
