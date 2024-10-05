
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

    other_addresses = addresses_from_points

    # Попытка получить ответ с addresses_from_points
    response = requests.post(api_url, headers=headers, data=json.dumps(addresses_from_locality), timeout=15)

    # Если ответ не 200, пробуем с addresses_from_locality
    if response.status_code != 200:
        # print(f"Ошибка при получении ID городов с addresses_from_points: {response.status_code}")
        response = requests.post(api_url, headers=headers, data=json.dumps(addresses_from_points), timeout=15)
        other_addresses = addresses_from_locality

    if response.status_code == 200:
        data = response.json()
        if data:
            processed_addresses = []
            for index, (address, value) in enumerate(data.items()):
                if value.get("is_success"):
                    city_id = value.get("city_id")
                    street = value.get("street")
                    if city_id is not None and city_id != 1020:
                        processed_addresses.append({"city_id": city_id, "street": street, address: address})
                    else:
                        # Существующая логика для получения city_id из locality
                        other_address = other_addresses[index]
                        other_response = requests.post(api_url, headers=headers, data=json.dumps([other_address]), timeout=15)
                        if other_response.status_code == 200:
                            other_data = other_response.json()
                            other_value = other_data.get(other_address, {})
                            if other_value.get("is_success"):
                                other_city_id = other_value.get("city_id")
                                if other_city_id is not None and other_city_id != 1020:
                                    processed_addresses.append({"city_id": other_city_id, "street": other_value.get("street"), address: other_address})
                                else:
                                    raise ValueError(f"City ID not found for both addresses: {address} and {locality_address}")
                            else:
                                raise ValueError(f"Failed to get city ID for both addresses: {address} and {locality_address}")
                        else:
                            processed_addresses.append(None)
                            print(f"Error getting city ID for locality address: {locality_address}")
                else:
                    processed_addresses.append(None)
                    print(f"Failed to get city ID for address: {address}")

            return processed_addresses
        else:
            print("Некорректные данные от API")
            return None
    else:
        print(f"Ошибка при получении ID городов: {response.status_code}")
        # print("addresses_from_points:", addresses_from_points)
        # print("addresses_from_locality:", addresses_from_locality)
        return None

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
    addresses_from_points = []
    
    for index, point in enumerate(order['routePoint']):
        
        # Find the corresponding locality for this point
        locality = next((loc for loc in data['locality'] if loc['id'] == point['storage']['code']), None)

        coordinates = None
        if locality and locality.get("coordinates"):
            coordinates = {
                "longitude": locality["coordinates"].get("longitude"),
                "latitude": locality["coordinates"].get("latitude")
            }
        elif point["storage"].get("coordinate"):
            coordinates = {
                "longitude": point["storage"]["coordinate"].get("longitude"),
                "latitude": point["storage"]["coordinate"].get("latitude")
            }
        
        processed_point = {
            "type": "loading" if point["type"] == "load" else "unloading",
            "location": {
                "type": "manual",   
                "coordinates": coordinates,
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
        addresses_from_points.append(point["storage"]["address"] if point["storage"].get("address") else locality["fullName"] if locality else "")    
   
    try:
        processed_addresses = get_city_ids(addresses_from_points, addresses_from_locality)
    except Exception as e:
        raise Exception(f"Error getting city IDs: {str(e)}")
    
    # Add city_ids to corresponding points
    for point, processed_address in zip(points, processed_addresses):
        point["location"]["city_id"] = processed_address.get('city_id')
        if processed_address.get('street'):
            point["location"]["address"] = processed_address['street']
        elif processed_address.get('city_id') == 1 and processed_address.get('address'):
            address = processed_address.get('address', '')
            address = address.lower().replace('город санкт-петербург', '').replace('г санкт-петербург', '').strip()
            point["location"]["address"] = address
        elif processed_address.get('city_id') == 3611 and processed_address.get('address'):
            address = processed_address.get('address', '')
            address = address.lower().replace('город москва', '').replace('г москва', '').strip()
            point["location"]["address"] = address

    return {
        "loading": {**points[0], "cargos": cargos},
        "unloading": points[-1],
        "way_points": points[1:-1] if len(points) > 2 else None
    }
