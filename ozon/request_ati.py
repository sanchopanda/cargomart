import os
from ozon_parser import format_waypoints
from type import loadingTypes, truckTypes

from dotenv import load_dotenv

load_dotenv()
BORD_ID = os.getenv("BORD_ID")

def create_request_body(data):
    if data:
        formatted_waypoints = format_waypoints(data["Route"]["WayPoints"], data)
        route = {
            "loading": formatted_waypoints[0],
            "unloading": formatted_waypoints[-1],
            "way_points": formatted_waypoints[1:-1]
        }

# Определяем тип кузова в зависимости от значения Name в Temperature
        temperature_name = data.get("Temperature", {}).get("Name", "")
        if temperature_name == "Не требуется":
            body_type = truckTypes[5]  # Тент
        else:
            body_type = truckTypes[4]  # Рефрижератор

        request_body = {
            "external_id": data["ID"],
            "route": route,
            "truck": {
                "trucks_count": 1,
                "load_type": "ftl",
                "body_types": body_type,
                "body_loading": {
                    "types": loadingTypes[2],
                    "is_all_required": True
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
                "type": "without-bargaining",
                "currency_type": 1,
                "rate_with_vat": int(round((data["ProcedureInfo"]["StartPrice"] / 100) * 0.85, -2)),
                "rate_without_vat": int(round((data["ProcedureInfo"]["StartPrice"] / 100) * 0.85 / 1.2, -2))
            },
            "boards": [
                {
                    "id": os.getenv("BORD_ID"),
                    "reservation_enabled": False
                }
            ]
        }
        return request_body
    return {}