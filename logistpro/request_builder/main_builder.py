import os
import logging
from .converter import convert_to_single
from .waypoints_builder import build_ati_waypoints

def create_request_body(parsed_application):
    """Создает тело запроса на основе распарсенных данных заявки."""
    try:
        waypoints = parsed_application.get('WayPoints', [])
        ati_waypoints = build_ati_waypoints(waypoints, parsed_application)

        loading_waypoints = [wp for wp in ati_waypoints if wp.get('type') == 'loading']
        unloading_waypoints = [wp for wp in ati_waypoints if wp.get('type') == 'unloading']

        # Обработка way_points согласно требованиям
        if len(ati_waypoints) > 2:
            processed_waypoints = ati_waypoints[1:-1]
        else:
            processed_waypoints = None

        route = {
            "loading": loading_waypoints[0] if loading_waypoints else {},
            "unloading": unloading_waypoints[-1] if unloading_waypoints else {},
            "is_round_trip": False
        }

        if processed_waypoints:
            route["way_points"] = processed_waypoints

        if parsed_application.get('InitCost') is None:
            print(f"Warning: 'currentPrice' not found for order {parsed_application.get('Id')}")
            return None

        request_body = {
            "external_id": f"https://lk.logistpro.su/Tender/Details/{parsed_application.get('Id')}",
            "route": route,
            "truck": {
                "trucks_count": 1,
                "load_type": "ftl",
                "body_types": [parsed_application.get('CargoTypeID')],
                "body_loading": {
                    "types": [parsed_application.get('LoadingTypeID')],
                    "is_all_required": True
                },
                "body_unloading": {
                    "types": [parsed_application.get('LoadingTypeID')],
                    "is_all_required": True
                }
            },
            "payment": {
                "type": "without-bargaining",
                "currency_type": 1,
                "rate_with_vat": int(round(convert_to_single(parsed_application.get('InitCost')) * 0.85, -2)),
                "rate_without_vat": int(round(convert_to_single(parsed_application.get('InitCost')) * 0.85 / 1.2, -2))
            },
            "boards": [
                {
                    "id": os.getenv('BOARD_ID'),
                    "reservation_enabled": False
                }
            ]
        }

        return request_body
    except KeyError as e:
        logging.error(f"Отсутствует ключ: {e} в parsed_application: {parsed_application.get('Id', 'Не указано')}")
        return None
    except Exception as e:
        logging.exception(f"Неизвестная ошибка при создании тела запроса для заявки: {parsed_application.get('Id', 'Не указано')}: {e}")
        return None