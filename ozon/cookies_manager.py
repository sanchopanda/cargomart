import os
import json
from login import get_cookies_from_selenium

# Функция для загрузки куки из файла
def load_cookies():
    cookies_file = "cookies.json"
    if os.path.exists(cookies_file):
        with open(cookies_file, "r", encoding="utf-8") as f:
            cookies = json.load(f)
            if cookies:  # Проверка, что файл не пустой
                print("Куки загружены из файла.")
                return cookies
            else:
                print("Файл куки пустой. Получаем новые куки...")
    else:
        print("Файл куки не найден. Получаем новые куки...")

    # Если файл не существует или пустой, получаем куки
    cookies = get_cookies_from_selenium()
    return cookies

# Функция для формирования заголовков с куки
def get_headers(cookies):
    return {
        "Content-Type": "application/json",
        "Cookie": (
            f"abt_data={cookies.get('abt_data')}; "
            f"__Secure-access-token={cookies.get('__Secure-access-token')}; "
            f"__Secure-refresh-token={cookies.get('__Secure-refresh-token')}; "
            f"__Secure-ab-group={cookies.get('__Secure-ab-group')}; "
            f"__Secure-user-id={cookies.get('__Secure-user-id')}; "
            f"TSDK_trackerSessionId={cookies.get('TSDK_trackerSessionId')}; "
            f"rfuid={cookies.get('rfuid')}; "
            f"is_adult_confirmed={cookies.get('is_adult_confirmed')}; "
            f"is_alco_adult_confirmed={cookies.get('is_alco_adult_confirmed')}; "
            f"X-O3-INGRESSCOOKIE={cookies.get('X-O3-INGRESSCOOKIE')}"
        )
    }
