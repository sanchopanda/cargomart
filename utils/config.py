import os
import platform
from selenium.webdriver.chrome.options import Options

script_dir = os.path.dirname(os.path.abspath(__file__))

# Путь к chromedriver
if platform.system() == 'Windows':
    chrome_driver_path = os.path.join(script_dir, '../chromedriver-win64', 'chromedriver.exe')
elif platform.system() == 'Darwin':  # macOS
    chrome_driver_path = os.path.join(script_dir, '../chromedriver-mac-arm64', 'chromedriver')
else:
    raise Exception("Неизвестная ОС. Не могу найти драйвер для Chrome.")


# Настройки Chrome
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
