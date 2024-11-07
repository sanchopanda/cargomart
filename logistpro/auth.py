from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from logistpro.cookie_manager import save_cookies
from logistpro.config import LOGIN_URL, MAIN_URL, SELENIUM_WAIT_TIMEOUT
from utils.config import chrome_driver_path, chrome_options
from dotenv import load_dotenv
import logging

load_dotenv()

# Настройка логирования
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def login_and_save_cookies(cookie_file):
    """Функция для авторизации через Selenium и сохранения кук.

    Args:
        cookie_file (str): Путь к файлу для сохранения кук.
    """
    logger.info("Запуск процесса авторизации через Selenium.")
    
    # Настройки драйвера Chrome
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # запуск без интерфейса, если нужно
    service = Service(executable_path=chrome_driver_path, )
    
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        logger.error(f"Не удалось инициализировать WebDriver: {e}")
        return

    driver.get(LOGIN_URL)  # URL страницы входа
    logger.info(f"Открыт URL: {LOGIN_URL}")

    try:
        # Ввод логина и пароля
        logger.info("Ввод логина и пароля.")
        # username = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.ID, "UserName"))
        # )
        # password = driver.find_element(By.ID, "Password")
        # username.send_keys(os.getenv("LOGIN"))
        # password.send_keys(os.getenv("PASSWORD"))
        # logger.info("Логин и пароль введены.")

        # Дождаться вручную прохождения капчи и нажатия на кнопку входа
        logger.info("Пройдите капчу и нажмите 'Войти'.")
        print("Пройдите капчу и нажмите 'Войти'.")

        # Ожидание перенаправления на главную страницу после авторизации
        WebDriverWait(driver, SELENIUM_WAIT_TIMEOUT).until(
            EC.url_to_be(MAIN_URL)  # Проверяем переход на URL главной страницы
        )
        logger.info("Авторизация прошла успешно!")

    except Exception as e:
        logger.error(f"Ошибка в процессе авторизации: {e}")
    finally:
        # Сохраняем куки после успешного перехода
        try:
            save_cookies(driver, cookie_file)
            logger.info(f"Куки сохранены в {cookie_file}.")
        except Exception as e:
            logger.error(f"Не удалось сохранить куки: {e}")
        driver.quit()
        logger.info("Браузер закрыт.")

# Добавляем возможность запуска скрипта отдельно для отладки
if __name__ == "__main__":
    from config import COOKIE_FILE
    login_and_save_cookies(COOKIE_FILE)