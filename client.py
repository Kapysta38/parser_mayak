import os
import logging
import traceback

import yaml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

file_log = logging.FileHandler('log_client.log', encoding='utf-8')
logging.basicConfig(handlers=(file_log,),
                    format='[%(asctime)s | %(levelname)s | %(name)s]: %(message)s',
                    datefmt='%m.%d.%Y %H:%M:%S',
                    level=logging.INFO)

log = logging.getLogger("parser-bot")

config_file = yaml.safe_load(open('config.yml', encoding='utf-8'))


class Client:
    LOGIN = config_file['client']['LOGIN']
    PASSWORD = config_file['client']['PASSWORD']

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-blink-features=AutomationController")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-notifications')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--disable-gpu")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument(f"user-data-dir={os.getcwd()}/cookie")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.driver.implicitly_wait(5)
        self.driver.set_window_size(1920, 1080)

    def first_login(self):
        try:
            inputs = self.driver.find_elements(By.CLASS_NAME, 'form-control')
            inputs[0].send_keys(self.LOGIN)
            inputs[1].send_keys(self.PASSWORD + Keys.ENTER)
            if 'Только для зарегистрированных клиентов.' not in self.driver.find_element(By.TAG_NAME, 'body').text:
                return True
            return False
        except Exception as ex:
            log.error({"ERROR": ex, 'TRACEBACK': traceback.format_exc()})
            return False

    def login(self):
        self.driver.get('https://app.mayak.bz/users/sign_in')
        if 'Только для зарегистрированных клиентов.' in self.driver.find_element(By.TAG_NAME, 'body').text:
            return self.first_login()
        else:
            return True

    def parse_url(self, url):
        try:
            self.driver.get(url)
            elem = self.driver.find_element(By.CLASS_NAME, 'table-footer.table-bordered')
            sells = elem.find_element(By.CLASS_NAME, 'text-right').text.replace(' шт.', '')
            if not sells.isdigit():
                sells = ''
            else:
                sells = int(sells)

            left = self.driver.find_element(By.CLASS_NAME, 'fixed-table-body')
            left = left.find_elements(By.TAG_NAME, 'tr')[-1]
            left = left.find_elements(By.CLASS_NAME, 'text-right')[1].text
            if not left.isdigit():
                left = ''
            else:
                left = int(left)

            return left, sells
        except Exception as ex:
            print('Произошла какая-то ошибка, отправьте файл log.log разработчику')
            log.error({"ERROR": ex, 'TRACEBACK': traceback.format_exc()})
            return '', ''

    def quit(self):
        self.driver.quit()
