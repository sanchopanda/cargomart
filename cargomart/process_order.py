def process_orders(response):
    processed_orders = []

    # Проход по всем заказам
    for order in response['order']:
        processed_order = {
            'id': order['id'],
            'status': next(
                (status['name'] for status in response['status'] if status['id'] == order['statusId']), None),
            'startDate': order['startDate'],
            'endDate': order.get('endDate', None),
            'cargoWeight': order['cargoWeight'],
            'cargoCapacity': order['cargoCapacity'],
            'loadWeight': order['loadWeight'],
            'loadCapacity': order['loadCapacity'],
            'type': order['type'],
            'truckType': next(
                (truck['name'] for truck in response['truckType'] if truck['id'] == order['truckTypeId']),
                None),
            'points': []
        }

        # Обработка пунктов назначения
        for point in order.get('point', []):
            locality = next((loc for loc in response['locality'] if loc['id'] == point['code']), {})
            processed_order['points'].append({**point, **locality})  # Объединяем данные из point и locality

        processed_orders.append(processed_order)

    return processed_orders