import os
import json

script_dir = os.path.dirname(os.path.abspath(__file__))

cookies_file = os.path.join(script_dir, './cookies.json')

def load_cookies(driver):
    if os.path.exists(cookies_file):
        with open(cookies_file, 'r', encoding='utf-8') as file:
            try:
                cookies = json.load(file)
                for cookie in cookies:
                    driver.add_cookie(cookie)
                print("Cookies успешно загружены.")
            except json.JSONDecodeError:
                print("Ошибка при загрузке cookies.")


def save_cookies(driver):
    cookies = driver.get_cookies()
    with open(cookies_file, 'w', encoding='utf-8') as file:
        json.dump(cookies, file, indent=4, ensure_ascii=False)
    print("Cookies успешно сохранены.")