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
import gspread
from dadata import Dadata
import re
from google.oauth2.service_account import Credentials
import platform


script_dir = os.path.dirname(os.path.abspath(__file__))

# Dadata
token = "8b98a136687412491cf220d96838f48ffc495178"
secret = "02a6d8e26bdaf701c89035cdc49024f7d6c324f5"
dadata = Dadata(token, secret)

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
chrome_options.add_argument("--headless")  # Запуск без интерфейса

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

creds_path = os.path.join(script_dir, 'credentials.json')

spreadsheet_name = 'Logist Pro'

# Укажите scopes
scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

# Загрузка учетных данных и авторизация
try:
    creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
    client = gspread.authorize(creds)
    spreadsheet = client.open(spreadsheet_name)
    worksheet = spreadsheet.sheet1  # Открываем первый лист
    print("Успешно подключились к Google Sheets.")
except Exception as e:
    print(f"Ошибка подключения к Google Sheets: {e}")
    driver.quit()
    exit()

# Определение заголовков столбцов
headers = ['ID', 'Тип груза', 'Тип кузова', 'Дата', 'Вес', 'Загрузка', 'Страна загрузки', 'Населенный пункт загрузки', 'Выгрузка', 'Страна выгрузки', 'Населенный пункт выгрузки', 'Ставка', 'Фирма', 'Город', 'Телефон']

# Проверка, существуют ли уже заголовки в первой строке
try:
    existing_headers = worksheet.row_values(1)  # Получаем первую строку (заголовки)
    
    # Если первая строка пустая, добавляем заголовки
    if not existing_headers:
        worksheet.append_row(headers)
except Exception as e:
    print(f"Ошибка при проверке или добавлении заголовков в Google Sheets: {e}")
    driver.quit()
    exit()

# Функция для экспорта данных в Google Sheets
def export_to_google_sheets(order_data):
    order_id = order_data.get('order_id', 'NONE')
    if worksheet.row_count == 0:
        worksheet.append_row(headers)

    # Проверка на наличие ID в обработанных
    if order_id in processed_orders:
        print(f"Заявка с ID {order_id} уже обработана. Пропускаем.")
        return
    
    try:
        row = [
            order_id,
            order_data.get('cargo_type', 'NONE'),
            order_data.get('body_type', 'NONE'),
            order_data.get('date', 'NONE'),
            order_data.get('weight', 'NONE'),
            order_data.get('loading', 'NONE'),
            order_data.get('loading_country', 'NONE'),
            order_data.get('loading_settlement', 'NONE'),
            order_data.get('unloading', 'NONE'),
            order_data.get('unloading_country', 'NONE'),
            order_data.get('unloading_settlement', 'NONE'),
            order_data.get('bet', 'NONE'),
            order_data.get('company', 'NONE'),
            order_data.get('city', 'NONE'),
            order_data.get('phone', 'NONE')
        ]
        worksheet.append_row(row)
        print("Данные успешно записаны.")
        
        # Добавление ID в список обработанных и сохранение
        processed_orders.append(order_id)
        save_processed_orders(processed_orders)
        print(f"ID {order_id} добавлен в обработанные заявки.")
    except Exception as e:
        print(f"Ошибка при добавлении данных в Google Sheets: {e}")

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
def format_date(date):
    # Определяем текущий год
    current_year = datetime.datetime.now().year
    
    # Создаем словарь для преобразования названий месяцев
    months = {
        "янв": "01",
        "фев": "02",
        "мар": "03",
        "апр": "04",
        "май": "05",
        "июн": "06",
        "июл": "07",
        "авг": "08",
        "сен": "09",
        "окт": "10",
        "ноя": "11",
        "дек": "12"
    }

    # Разбиваем дату на части
    parts = date.split(' ')
    day = parts[0]
    month = months.get(parts[1].lower(), '01')  # Получаем числовое значение месяца
    time = parts[2]

    # Формируем дату в формате дд.мм.гггг чч:мм
    formatted_date = f"{day}.{month}.{current_year} {time}"
    
    return formatted_date

# Функция парсинга данных заявки
def parse_order_details():
    try:
        order_id = driver.find_element(By.CSS_SELECTOR, '[data-test="order-serial"]').text or 'NONE'
        order_id = order_id.replace('№', '').strip()
    except Exception as e:
        print(f"Ошибка при извлечении ID заявки: {e}")
        order_id = 'NONE'
    
    # Обновляем индексы на 0 и 1 для груза и веса
    try:
        spans = driver.find_elements(By.CSS_SELECTOR, "span.mt-2")
        
        cargo_type = spans[0].text.strip() if len(spans) > 0 else 'NONE'
        weight_volume = spans[1].text.strip() if len(spans) > 1 else 'NONE'
        
        # Разделение веса до знака '/'
        weight = weight_volume.split('/')[0].strip() if '/' in weight_volume else weight_volume
    except Exception as e:
        print(f"Ошибка при извлечении типа груза и веса: {e}")
        cargo_type = 'NONE'
        weight = 'NONE'
    
    try:
        body_type = driver.find_element(By.CSS_SELECTOR, "div.truncate.mb-1.text-body-sm").text or 'NONE'
    except Exception as e:
        print(f"Ошибка при извлечении типа кузова: {e}")
        body_type = 'NONE'
    
    try:
        date = driver.find_element(By.CSS_SELECTOR, "p.truncate.text-on-surface-variant").text or 'NONE'
        date = format_date(date)
    except Exception as e:
        print(f"Ошибка при извлечении даты: {e}")
        date = 'NONE'

    try:
        loading = driver.execute_script("""
            var element = arguments[0];
            return element.childNodes[0].nodeValue.trim();
        """, driver.find_element(By.CSS_SELECTOR, "div.flex.mt-2 .flex.flex-col .flex.flex-col .flex.flex-col"))

        # Если текст пустой, заменяем его на 'NONE'
        loading = loading or 'NONE'
        print(f"Адрес загрузки до обработки: {loading}")

        # Используем DaData для поиска адреса
        address_data = dadata.suggest("address", loading)
        address_info = address_data[0]['data']

        # Извлекаем данные о стране и населённом пункте
        loading_country = address_info.get('country')
        loading_settlement = address_info.get('city_with_type')
    except Exception as e:
        print(f"Ошибка при обработке адреса загрузки: {e}")
        loading = 'NONE'  

    try:
        unloading = driver.execute_script("""
            var element = arguments[0];
            return element.childNodes[0].nodeValue.trim();
        """, driver.find_element(By.CSS_SELECTOR, "div.flex.mt-4 .flex.flex-col .flex.flex-col .flex.flex-col"))
        unloading = unloading or 'NONE'
        address_data = dadata.suggest("address", unloading)
        address_info = address_data[0]['data']
            
        # Извлекаем данные о стране, типе и названии населенного пункта
        unloading_country = address_info.get('country')
        unloading_settlement = address_info.get('city_with_type')
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
    
    # Возвращаем словарь с данными
    return {
        "order_id": order_id,
        "cargo_type": cargo_type,
        "body_type": body_type,
        "date": date,
        "weight": weight,
        "loading": loading,
        "loading_country": loading_country,
        "loading_settlement": loading_settlement,
        "unloading": unloading,
        "unloading_country": unloading_country,
        "unloading_settlement": unloading_settlement,
        "bet": bet,
        "company": company,
        "city": city,
        "phone": phone
    }

# Переход на страницу заявок и парсинг каждой заявки
def process_orders():
    while True:
        try:
            orders = driver.find_elements(By.CSS_SELECTOR, '[data-name="tableRow"]')
            print(f"Найдено {len(orders)} заявок.")
            
            for order in orders:
                try:
                    order.click()  # Открываем заявку
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test="order-serial"]')))
                    
                    # Парсинг данных с заявки
                    order_data = parse_order_details()
                    
                    # Проверка на наличие ID в обработанных
                    if order_data.get('order_id') in processed_orders:
                        print(f"Заявка с ID {order_data.get('order_id')} уже обработана. Приостановка на 40 секунд.")
                        driver.refresh()  # Обновление страницы
                        time.sleep(40)  # Ожидание 40 секунд минут
                        break  # Прерываем цикл, чтобы начать заново после обновления страницы
                    
                    export_to_google_sheets(order_data)
                    
                    # Возврат к списку заявок
                    driver.back()
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-name="tableRow"]')))
                except Exception as e:
                    pass
            
            # Проверяем, есть ли еще заявки для обработки
            if not orders:
                print("Нет заявок для обработки. Завершение.")
                break

        except Exception as e:
            print(f"Ошибка при получении списка заявок: {e}")
            break

# Основной блок выполнения
try:
    process_orders()
finally:
    print("Парсинг завершен.")
    driver.quit()