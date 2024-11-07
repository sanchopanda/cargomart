import logging
import json
from logistpro.parser import parse_application
from logistpro.request_builder import create_request_body

def process_applications(data, authorization_token):
    """Обрабатывает список заявок и создает тела запросов.

    Args:
        data (dict): Сырые данные с заявками.
        authorization_token (str): Токен авторизации для API.

    Returns:
        tuple: Словарь распарсенных заявок и словарь тел запросов.
    """
 
    request_bodies = {}  # Словарь для хранения тел запросов

    for application in data.get('Items', []):
        parsed_application = parse_application(application, authorization_token)
        if parsed_application:
            # Создаем тело запроса
            request_body = create_request_body(parsed_application)
            request_bodies[request_body.get('external_id')] = request_body

    return request_bodies