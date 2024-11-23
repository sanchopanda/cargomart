from logistpro.parser.transport_parser import convert_date  # Импортируем функцию convert_date

def build_ati_waypoints(waypoints, parsed_application):
    """Создает список waypoints для ATI API с добавлением информации о грузе."""
    ati_waypoints = []
    cargo_added = False

    for index, wp in enumerate(waypoints):
        # Конвертация даты
        # first_date = wp.get("date", "Не указано")
        # if first_date != "Не указано":
        #     first_date = convert_date(first_date)

        # Создаем базовый словарь way_point без поля 'address'
        way_point = {
            "type": wp.get('type', 'Не указано'),
            "location": {
                "type": "manual",
                "city_id": wp.get('city_id', 'Не указано'),
            },
            "dates": {
                "type": "from-date" if index == 0 else None,
                "time": {
                    "type": "bounded",
                    "start": wp.get("time_start", "Не указано"),
                    #"end": wp.get("time_end") if wp.get("time_end") else None
                },
                "first_date": wp.get("date", None),
                "last_date":  wp.get("date", None)
            }
        }
# Добавляем 'end', только если оно присутствует и не пустое
        time_end = wp.get("time_end")
        if time_end:
            way_point["dates"]["time"]["end"] = time_end
        # Добавляем 'address', только если он присутствует и не пустой
        address = wp.get('address')
        if address:
            way_point["location"]["address"] = address

        # Добавляем информацию о грузе для загрузочных точек
        if wp.get('type') == 'loading' and not cargo_added:
            way_point["cargos"] = [
                {
                    "id": 1,
                    "name": parsed_application.get('CargoType', 'Не указано'),
                    "weight": {
                        "type": "tons",
                        "quantity": parsed_application.get('CargoWeight', 'Не указано')
                    },
                    "volume": {
                        "quantity": parsed_application.get('CargoValue', 'Не указано')
                    }
                }
            ]

            cargo_added = True

        ati_waypoints.append(way_point)

    return ati_waypoints