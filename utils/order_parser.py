from selenium.webdriver.common.by import By
from utils.format_date import format_date
import re

def parse_order_details(driver):
    try:
        order_id = driver.find_element(By.CSS_SELECTOR, '[data-test="order-serial"]').text or 'NONE'
        order_id = order_id.replace('№', '').strip()

        print(f"ID заявки: {order_id}")

    except Exception as e:
        print(f"Ошибка при извлечении ID заявки: {e}")
        order_id = 'NONE'
    
    # Тип груза
    try:
        spans = driver.find_elements(By.CSS_SELECTOR, "span.mt-2")
        cargo_type = spans[0].text.strip() if len(spans) > 0 else 'NONE'
    except Exception as e:
        print(f"Ошибка при извлечении типа груза: {e}")
        cargo_type = 'NONE'

    #Вес и объем
    try:
        spans = driver.find_elements(By.CSS_SELECTOR, "span.mt-2")
        
        if len(spans) > 1:
            weight_volume = spans[1].text.strip()
            # Разделение на вес и объем, если есть разделитель "/"
            if '/' in weight_volume:
                weight, volume = weight_volume.split('/')
                weight = weight.strip()
                volume = volume.strip()
                # Очистка веса от букв и оставляем только цифры и точку
                weight = re.sub(r'[^\d.,]', '', weight)
                volume = re.sub(r'[^\d.,]', '', volume)
            else:
                weight = re.sub(r'[^\d.,]', '', weight_volume)  # Если объема нет, берем только вес
                volume = 'NONE'
        else:
            weight = 'NONE'
            volume = 'NONE'
    except Exception as e:
        print(f"Ошибка при извлечении данных веса и объема: {e}")
        weight = 'NONE'
        volume = 'NONE'

    
    try:
        body_type = driver.find_element(By.CSS_SELECTOR, "div.truncate.mb-1.text-body-sm").text or 'NONE'
    except Exception as e:
        print(f"Ошибка при извлечении типа кузова: {e}")
        body_type = 'NONE'
    
    # Дата 1
    try:
        # Извлечение даты с помощью JavaScript
        date_element = driver.find_element(By.CSS_SELECTOR, "div.flex.mt-2 .flex.flex-col .text-primary")
        date = driver.execute_script("return arguments[0].childNodes[0].nodeValue.trim();", date_element)

        if len(date) > 12:
            date = date[:12]
        print(f"Полученная дата загрузки: {date}")

        # Передаем извлеченную строку в функцию обработки
        formatted_date_loading, time_start_loading, time_end_loading = format_date(date)
        
    except Exception as e:
        print(f"Ошибка при обработке даты загрузки: {e}")

    # Дата 2
    try:
        # Извлечение даты с помощью JavaScript
        date2_element = driver.find_element(By.CSS_SELECTOR, "div.flex.mt-4 .flex.flex-col .text-primary")
        date2 = driver.execute_script("return arguments[0].childNodes[0].nodeValue.trim();", date2_element)

        if len(date2) > 12:
            date2 = date2[:12]
        print(f"Полученная дата выгрузки: {date2}")

        # Передаем извлеченную строку в функцию обработки
        formatted_date_unloading, time_start_unloading, time_end_unloading = format_date(date2)
        
    except Exception as e:
        print(f"Ошибка при обработке даты выгрузки: {e}")

    try:
        loading = driver.execute_script("""
            var element = arguments[0];
            return element.childNodes[0].nodeValue.trim();
        """, driver.find_element(By.CSS_SELECTOR, "div.flex.mt-2 .flex.flex-col .flex.flex-col .flex.flex-col"))

        print(f"Адрес загрузки до обработки: {loading}")

    except Exception as e:
        loading = 'NONE'  

    try:
        unloading = driver.execute_script("""
            var element = arguments[0];
            return element.childNodes[0].nodeValue.trim();
        """, driver.find_element(By.CSS_SELECTOR, "div.flex.mt-4 .flex.flex-col .flex.flex-col .flex.flex-col"))
    except Exception as e:
        print(f"Ошибка при обработке адреса выгрузки: {e}")
        unloading = 'NONE'
    
    try:
        bet = driver.find_element(By.CSS_SELECTOR, "span.flex.items-center").text or 'NONE'
        bet = re.sub(r'[^\d,]', '', bet).replace('\n', '').replace(',', '.')
    except Exception as e:
        print(f"Ошибка при извлечении ставки: {e}")
        bet = 'NONE'

    # Фиксированные значения
    company = 'ООО "Фортуна-Аэро-Карго"'
    city = 'Москва'
    phone = '+79613423284'
    
    # create_application({
    #     'order_id': order_id,
    #     'loading': loading,
    #     'unloading': unloading,
    #     'cargo_type': cargo_type,
    #     'weight': weight,
    #     'volume': volume,
    #     'bet': bet,
    #     'formatted_date_loading': formatted_date_loading,
    #     'time_start_loading': time_start_loading,
    #     'time_end_loading': time_end_loading,
    #     'formatted_date_unloading': formatted_date_unloading,
    #     'time_start_unloading': time_start_unloading,
    #     'time_end_unloading': time_end_unloading
    # })

    # Возвращаем словарь с данными
    return {
        "order_id": order_id,
        "cargo_type": cargo_type,
        "body_type": body_type,
        "date_loading": formatted_date_loading,
        "time_start_loading": time_start_loading,
        "time_end_loading": time_end_loading,
        "date_unloading": formatted_date_unloading,
        "time_start_unloading": time_start_unloading,
        "time_end_unloading": time_end_unloading,
        "weight": weight,
        "volume": volume,
        "loading": loading,
        "unloading": unloading,
        "bet": bet,
        "company": company,
        "city": city,
        "phone": phone
    }

