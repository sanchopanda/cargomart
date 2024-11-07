import pickle

def save_cookies(driver, path):
    """Сохраняет куки из драйвера в файл.

    Args:
        driver (webdriver): Selenium WebDriver.
        path (str): Путь к файлу для сохранения кук.
    """
    cookies = driver.get_cookies()
    print("Куки для сохранения:", cookies)  # Отладка для проверки
    if cookies:
        with open(path, 'wb') as file:
            pickle.dump(cookies, file)
    else:
        print("Куки пустые. Авторизация могла завершиться неудачно.")

def load_cookies(path):
    """Загружает куки из файла.

    Args:
        path (str): Путь к файлу с куками.

    Returns:
        list: Список кук.
    """
    with open(path, 'rb') as file:
        return pickle.load(file)