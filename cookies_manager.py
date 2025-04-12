import json

cookies_file = 'cargomart/cookies.json'

def save_cookies(driver):
    """Сохраняет cookies в файл в виде строки"""
    cookies = driver.get_cookies()
    cookie_string = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
    
    with open(cookies_file, 'w') as file:
        json.dump({'cookie_string': cookie_string}, file)

def load_cookies(driver):
    """Загружает cookies из файла и устанавливает их в браузер"""
    try:
        with open(cookies_file, 'r') as file:
            data = json.load(file)
            cookie_string = data.get('cookie_string', '')
            
            if cookie_string:
                # Разбираем строку cookies на отдельные куки
                cookie_pairs = cookie_string.split('; ')
                for pair in cookie_pairs:
                    name, value = pair.split('=', 1)
                    driver.add_cookie({
                        'name': name,
                        'value': value,
                        'domain': '.cargomart.ru'  # Домен должен соответствовать сайту
                    })
                return True
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return False