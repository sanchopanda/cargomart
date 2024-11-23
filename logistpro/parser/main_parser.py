import logging
import json
from logistpro.api_client import fetch_city_ids
from .cargo_parser import parse_cargo_parameters
from .transport_parser import parse_transport_summary, convert_date
from .route_parser import parse_route


def parse_application(application, authorization_token):
    """Обрабатывает заявку и возвращает структурированные данные."""
    application_id = application.get('Id', 'Не указано')

    transport_summary = application.get('TransportSummary', 'Не указано')
    route = application.get('Route', 'Не указано')
    cargo_parameters = application.get('CargoParameters', 'Не указано')

    # Парсинг TransportSummary
    cargo_type, loading_type = parse_transport_summary(transport_summary)

    # Словари для сопоставления
    cargo_type_mapping = {
        "Тент": 200,
        "Рефрижератор": 300,
        "Изотерм": 400,
        "Борт": 1100,
        "Тент/Борт": 200,
        "Трал": 10700,
        "Любой закрытый": 30000,
        "Любой открытый": 20000
    }

    loading_type_mapping = {
        "Задняя": 4,
        "Задня": 4,
        "задняя": 4,
        "Боковая": 2,
        "боковая": 2,
        "Бокова": 2
    }

    # Получение CargoTypeID и LoadingTypeID
    cargo_type_id = cargo_type_mapping.get(cargo_type, "Не указано")
    
    loading_type_id = loading_type_mapping.get(loading_type, "Не указано")

    # Парсинг маршрута
    waypoints = parse_route(route)

    # Обработка CargoParameters
    cargo_weight, cargo_value = parse_cargo_parameters(cargo_parameters)

    # Разделяем адреса на загрузочные и выгрузочные
    unique_loading_addresses = set(addr['address'] for addr in waypoints if addr['type'] == 'loading')
    unique_unloading_addresses = set(addr['address'] for addr in waypoints if addr['type'] == 'unloading')

    # Получаем CityID и Street для всех адресов
    city_info = fetch_city_ids(
        unique_loading_addresses=unique_loading_addresses,
        unique_unloading_addresses=unique_unloading_addresses,
        authorization_token=authorization_token
    )

    # Назначаем city_id и street каждой точке маршрута
    for wp in waypoints:
        original_address = wp.get('address', 'Не указано')
        info = city_info.get(original_address, {})
        wp['city_id'] = info.get('city_id', "Не указано")
        
        street = info.get('street')
        if street:
            wp['address'] = street
        else:
            wp.pop('address', None)  # Удаляем 'address', если 'street' отсутствует

    parsed_data = {
        'Id': application_id,
        'Number': application.get('Number', 'Не указано'),
        'InitCost': application.get('InitCostDec', 'Не указано'),
        'ProductType': application.get('Cargo', 'Не указано'),
        'CargoParameters': cargo_parameters,
        'CargoWeight': cargo_weight,
        'CargoValue': cargo_value,
        'CargoType': cargo_type,
        'CargoTypeID': cargo_type_id,
        'LoadingType': loading_type,
        'LoadingTypeID': loading_type_id,
        'WayPoints': waypoints
    }

    return parsed_data