from city_ids import get_city_ids
import logging

def format_waypoints(waypoints, data):
    addresses = [wp['Point']['Address'] for wp in waypoints]
    city_id_data = get_city_ids(addresses)  # Получаем city_id и форматированный адрес

    formatted_waypoints = []
    
    # Форматируем первый элемент
    first_wp = waypoints[0]
    first_address = first_wp['Point']['Address']
    first_city_info = city_id_data.get(first_address, {})
    
    first_location = {
        "type": "manual",
        "city_id": first_city_info.get("city_id"),
    }
    
    # Добавляем "address", только если форматированный адрес существует
    formatted_first_address = first_city_info.get("street", first_address)
    if formatted_first_address:
        first_location["address"] = formatted_first_address

    formatted_waypoints.append({
        "type": "loading",
        "city_id": first_city_info.get("city_id"),
        "location": first_location,
        "dates": {
            "type": "ready",
            "time": {
                "type": "bounded",
                "start": first_wp["ArrivalAt"].split("T")[1][:-1]
            },
            "first_date": first_wp["ArrivalAt"].split("T")[0]
        },
        "cargos": [
            {
                "id": 1,
                "name": "ТНП",
                "weight": {
                    "type": "tons",
                    "quantity": data["TransportType"]["Tonnage"]
                },
                "volume": {
                    "quantity": int(data["TransportType"]["Capacity"].split('.')[0])
                }
            }
        ]
    })
    
    # Форматируем остальные элементы
    for wp in waypoints[1:]:
        address = wp['Point']['Address']
        city_info = city_id_data.get(address, {})

        waypoint_data = {
            "type": wp["Actions"][0].lower(),
            "location": {
                "type": "manual",
                "city_id": city_info.get("city_id", None),
            },
            "dates": {
                "type": "ready",
                "time": {
                    "type": "bounded",
                    "start": wp["ArrivalAt"].split("T")[1][:-1]
                },
                "first_date": wp["ArrivalAt"].split("T")[0]
            }
        }

        # Добавляем "address", только если форматированный адрес существует
        formatted_address = city_info.get("street")
        if formatted_address:
            waypoint_data["location"]["address"] = formatted_address

        formatted_waypoints.append(waypoint_data)
        logging.info(f"Добавлен WayPoint: {waypoint_data}")

    return formatted_waypoints
    