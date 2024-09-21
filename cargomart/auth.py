from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from cargomart.cookies_manager import save_cookies, load_cookies

# Данные для авторизации
username = "a.ivanov@dsg-logist.ru"
password = "quCBdj4z"

def login(driver):
    # Загрузка cookies, если они существуют
    driver.get("https://cargomart.ru/login/")
    load_cookies(driver)

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
            save_cookies(driver)
        except Exception as e:
            print(f"Ошибка авторизации: {e}")
            driver.quit()
            exit()

