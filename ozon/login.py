import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from ozon.config import COOKIE_FILE, CHROME_DRIVER_PATH


def get_cookies_from_selenium():
    # Настройки для Selenium
    chrome_options = Options()
    #chrome_options.add_argument("--headless")  # Запуск в фоновом режиме
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Укажите путь к вашему драйверу
    service = Service(executable_path=CHROME_DRIVER_PATH)  # Укажите путь к ChromeDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Открываем страницу авторизации
    driver.get("https://tms.ozon.ru/ozi-orders")  # URL страницы авторизации

    # Ожидаем, пока пользователь введет логин и пароль и нажмет кнопку входа
    try:

        # Получаем куки
        cookies = driver.get_cookies()
        
        # Преобразуем куки в формат, подходящий для requests
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie['name']] = cookie['value']
        
        # Сохраняем куки в файл
        with open(COOKIE_FILE, "w", encoding="utf-8") as f:
            json.dump(cookie_dict, f, ensure_ascii=False, indent=4)

    finally:
        driver.quit()  # Закрываем веб-драйвер

    return cookie_dict
