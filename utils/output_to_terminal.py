def output_to_terminal(order_data):
    order_id = order_data.get('order_id', 'NONE')
    # Проверка на наличие ID в обработанных
    # if order_id in processed_orders:
    #     print(f"Заявка с ID {order_id} уже обработана. Пропускаем.")
    #     return

    try:
        # Выводим данные заявки в терминал
        print(f"\nЗаявка с ID: {order_id}")
        print(f"Тип груза: {order_data.get('cargo_type', 'NONE')}")
        print(f"Тип кузова: {order_data.get('body_type', 'NONE')}")
        print(f"Дата загрузки: {order_data.get('date_loading', 'NONE')}")
        print(f"Дата выгрузки: {order_data.get('date_unloading', 'NONE')}")
        print(f"Вес: {order_data.get('weight', 'NONE')}")
        print(f"Объем: {order_data.get('volume', 'NONE')}")
        print(f"Загрузка: {order_data.get('loading', 'NONE')}")
        print(f"Выгрузка: {order_data.get('unloading', 'NONE')}")
        print(f"Ставка: {order_data.get('bet', 'NONE')}")
        print(f"Фирма: {order_data.get('company', 'NONE')}")
        print(f"Город: {order_data.get('city', 'NONE')}")
        print(f"Телефон: {order_data.get('phone', 'NONE')}")

        
        # Добавление ID в список обработанных и сохранение
        # processed_orders.append(order_id)
        # save_processed_orders(processed_orders)
        print(f"ID {order_id} добавлен в обработанные заявки.")
    except Exception as e:
        print(f"Ошибка при обработке данных: {e}")
