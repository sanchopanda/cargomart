from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import datetime
import os
import json
import re
import platform
import traceback
from apitest import create_application  # Импортируй свою функцию

script_dir = os.path.dirname(os.path.abspath(__file__))

# Путь к вашему chromedriver
if platform.system() == 'Windows':
    chrome_driver_path = os.path.join(script_dir, 'chromedriver-win64', 'chromedriver.exe')
elif platform.system() == 'Darwin':  # macOS
    chrome_driver_path = os.path.join(script_dir, 'chromedriver-mac-arm64', 'chromedriver')
else:
    raise Exception("Неизвестная операционная система. Не могу найти подходящий драйвер для Chrome.")

print(f"Используемый драйвер: {chrome_driver_path}")

# Данные для авторизации
username = "a.ivanov@dsg-logist.ru"
password = "quCBdj4z"

# Настройки для Chrome
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--headless")  # Запуск без интерфейса

# Путь к файлу с cookies
cookies_file = os.path.join(script_dir, 'cookies.json')

# Инициализация Chrome Driver
print("Инициализация Chrome Driver...")
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Загрузка cookies, если они существуют
def load_cookies():
    if os.path.exists(cookies_file):
        with open(cookies_file, 'r', encoding='utf-8') as file:
            try:
                cookies = json.load(file)
                for cookie in cookies:
                    driver.add_cookie(cookie)
                print("Cookies успешно загружены.")
            except json.JSONDecodeError:
                print("Ошибка при загрузке cookies.")

# Сохранение cookies
def save_cookies():
    cookies = driver.get_cookies()
    with open(cookies_file, 'w', encoding='utf-8') as file:
        json.dump(cookies, file, indent=4, ensure_ascii=False)
    print("Cookies успешно сохранены.")

# Открытие страницы логина
print("Браузер запущен. Открытие страницы логина...")
driver.get("https://cargomart.ru/login/")

# Загрузка cookies, если они существуют
load_cookies()

# Если cookies не были загружены (например, при первом запуске), авторизация
if not driver.get_cookie("session"):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "login")))
        login_field = driver.find_element(By.NAME, "login")
        login_field.send_keys(username)
        print("Логин введен.")

        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys(password)
        print("Пароль введен.")

        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        print("Нажата кнопка Войти.")

        # Ожидание загрузки страницы после авторизации
        WebDriverWait(driver, 10).until(EC.url_contains("orders/active"))
        print("Успешная авторизация. Открыта страница заявок.")
        
        # Сохранение cookies после успешной авторизации
        save_cookies()
    except Exception as e:
        print(f"Ошибка авторизации: {e}")
        driver.quit()
        exit()


def output_to_terminal(order_data):
    order_id = order_data.get('order_id', 'NONE')
    # Проверка на наличие ID в обработанных
    if order_id in processed_orders:
        print(f"Заявка с ID {order_id} уже обработана. Пропускаем.")
        return

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
        processed_orders.append(order_id)
        save_processed_orders(processed_orders)
        print(f"ID {order_id} добавлен в обработанные заявки.")
    except Exception as e:
        print(f"Ошибка при обработке данных: {e}")

# Путь к файлу для хранения обработанных заявок
processed_orders_file = os.path.join(script_dir, 'processed_orders.json')

# Функция для загрузки обработанных заявок из файла
def load_processed_orders():
    if os.path.exists(processed_orders_file):
        with open(processed_orders_file, 'r', encoding='utf-8') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    return []

# Функция для записи обработанных заявок в файл
def save_processed_orders(processed_orders):
    with open(processed_orders_file, 'w', encoding='utf-8') as file:
        json.dump(processed_orders, file, indent=4, ensure_ascii=False)

# Загрузка обработанных заявок в память
processed_orders = load_processed_orders()

# Функция для преобразования даты
def format_date(date_str):
    # Определяем текущий год
    current_year = datetime.datetime.now().year

    # Словарь для преобразования названий месяцев
    months = {
        "янв": "01", "фев": "02", "мар": "03", "апр": "04",
        "май": "05", "июн": "06", "июл": "07", "авг": "08",
        "сен": "09", "окт": "10", "ноя": "11", "дек": "12"
    }

    try:
        # Разбиваем строку на части (например, '19 сен 03:00–05:00')
        parts = date_str.split()
        if len(parts) < 3:
            raise ValueError("Неверный формат даты. Ожидалось как минимум 3 части.")

        day = parts[0]  # День
        month = months.get(parts[1].lower(), '01')  # Месяц
        time_part = parts[2]  # Время (например, 03:00–05:00)

        # Форматируем дату в формате гггг-мм-дд
        formatted_date = f"{current_year}-{month}-{day}"

        # Проверяем, есть ли диапазон времени
        if '–' in time_part:
            start_time, end_time = time_part.split('–')
        else:
            start_time = time_part
            end_time = None

        # Возвращаем дату и диапазон времени
        return formatted_date, start_time, end_time
    except (IndexError, KeyError, ValueError) as e:
        print(f"Ошибка при обработке даты: {e}")
        return date_str, '00:00', '00:00'  # Если ошибка, возвращаем исходные значения


# Функция парсинга данных заявки
def parse_order_details():
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
    
    create_application({
        'order_id': order_id,
        'loading': loading,
        'unloading': unloading,
        'cargo_type': cargo_type,
        'weight': weight,
        'volume': volume,
        'bet': bet,
        'formatted_date_loading': formatted_date_loading,
        'time_start_loading': time_start_loading,
        'time_end_loading': time_end_loading,
        'formatted_date_unloading': formatted_date_unloading,
        'time_start_unloading': time_start_unloading,
        'time_end_unloading': time_end_unloading
    })

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


# Переход на страницу заявок и парсинг каждой заявки
def process_orders():
    while True:
        try:
            # Получаем список всех заявок на странице
            orders = driver.find_elements(By.CSS_SELECTOR, '[data-name="tableRow"]')[1:]
            print(f"Найдено {len(orders)} заявок.")
            
            for index in range(len(orders)):
                try:
                    # Обновляем список заявок, чтобы работать с актуальными элементами
                    orders = driver.find_elements(By.CSS_SELECTOR, '[data-name="tableRow"]')[1:]
                    
                    # Открытие заявки
                    print(f"Открытие заявки {index + 1}")
                    orders[index].click()  # Кликаем по заявке
                    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-test="order-serial"]')))

                    
                    # Парсинг данных с заявки
                    order_data = parse_order_details()
                    
                    # Проверка на наличие ID в обработанных
                    if order_data.get('order_id') in processed_orders:
                        print(f"Заявка с ID {order_data.get('order_id')} уже обработана. Пропускаем.")
                        driver.back()  # Возврат к списку заявок
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-name="tableRow"]')))
                        continue  # Переход к следующей заявке
                    
                    # Выводим данные заявки
                    output_to_terminal(order_data)
                                        
                    # Возврат к списку заявок
                    driver.back()
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-name="tableRow"]')))
                    
                except Exception as e:
                    print(f"Ошибка при обработке заявки: {str(e)}")
                    traceback.print_exc()
                    print("После обработки исключения")
                    driver.back()  # Возврат к списку заявок в случае ошибки
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-name="tableRow"]')))
            
            # Проверяем, есть ли еще заявки для обработки
            if not orders:
                print("Нет заявок для обработки. Завершение.")
                break

        except Exception as e:
            print(f"Ошибка при получении списка заявок: {str(e)}")
            break

# Основной блок выполнения
try:
    process_orders()
finally:
    print("Парсинг завершен.")
    driver.quit()