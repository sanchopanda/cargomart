import os
import logging

# Путь к драйверу Chrome
script_dir = os.path.dirname(os.path.abspath(__file__))
CHROME_DRIVER_PATH = os.path.join(script_dir, '../chromedriver-win64', 'chromedriver.exe')
COOKIE_FILE =  os.path.join(script_dir, './cookies.json')