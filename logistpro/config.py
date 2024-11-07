import os
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Пути к файлам
PROCESSED_IDS_FILE = 'processed_ids.json'


# URL-ы
ATI_API_URL = "https://api.ati.su/v1.0/dictionaries/locations/parse"
DATA_URL = "https://lk.logistpro.su/api/public/request?mode=Open&tenderType=Order&public=Show"
LOGIN_URL = "https://lk.logistpro.su/Account/Login"
MAIN_URL = "https://lk.logistpro.su/"

# Авторизационный токен
AUTHORIZATION_TOKEN = os.getenv('AUTHORIZATION_TOKEN', '012048bb93104026a60064f7b3898580')

# Путь к драйверу Chrome
script_dir = os.path.dirname(os.path.abspath(__file__))
CHROME_DRIVER_PATH = os.path.join(script_dir, './chromedriver-win64', 'chromedriver.exe')
COOKIE_FILE =  os.path.join(script_dir, './cookies.pkl')

# Настройки Selenium
SELENIUM_WAIT_TIMEOUT = 300

# Время ожидания в секундах