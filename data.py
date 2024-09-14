from dadata import Dadata

# Dadata токены
token = "2a7a0ad0255948c57cd026af350973c0b5137790"
secret = "534860360325aa528f93be32969ae0e9572aafea"
dadata = Dadata(token, secret)

# Пример неформатированного адреса
raw_address = 'Тульская обл, Ленинский р-н, деревня Варваровка, Варваровский проезд, стр 15Ф'

# Функция для форматирования адреса через DaData
def format_address(address):
    try:
        # Предполагается, что результат вызова dadata.suggest возвращает список
        address_data = dadata.suggest("address", address)
        
        if address_data:  # Проверяем, что список не пуст
            # Берем первый элемент списка, который содержит данные
            address_info = address_data[0]['data']
            
            # Извлекаем данные о стране, регионе, типе и названии населенного пункта
            country = address_info.get('country')
            region = address_info.get('region_with_type')
            settlement_type = address_info.get('settlement_type_full')
            settlement = address_info.get('settlement')
            
            # Форматируем и выводим адрес
            print(f"Форматированный адрес: {country}, {region}, {settlement_type}, {settlement}")
        else:
            print("Адрес не найден.")
    
    except Exception as e:
        print(f"Ошибка при форматировании адреса: {e}")


# Тест функции форматирования адреса
formatted_address = format_address(raw_address)