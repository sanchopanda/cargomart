import os
from ozon_parser import format_waypoints

def create_request_body(data):
    if data:
        formatted_waypoints = format_waypoints(data["Route"]["WayPoints"], data)
        route = {
            "loading": formatted_waypoints[0],
            "unloading": formatted_waypoints[-1],
            "way_points": formatted_waypoints[1:-1]
        }

        request_body = {
            "external_id": data["ID"],
            "route": route,
            "truck": {
                "trucks_count": 1,
                "load_type": "ftl",
                "body_types": "NULL",
                "body_loading": {
                    "types": "NULL",
                    "is_all_required": True
                },
                "body_unloading": {
                    "types": "NULL",
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
                "rate_with_vat": int((data["ProcedureInfo"]["StartPrice"]) / 100),
                "rate_without_vat": data["ProcedureInfo"]["Step"]
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