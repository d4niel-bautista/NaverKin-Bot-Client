from networking.service import Service
from crawler.session_manager import save_cookies, load_cookies, load_useragent, save_useragent
import undetected_chromedriver as uc

class Crawler():
    username = ''
    password = ''
    submit_delay = 60
    page_refresh = 300
    on_error = False
    stop = False
    service = None

    def __init__(self, service: Service):
        self.service = service
    
    def get_account(self):
        response = self.service.get_account()
        if type(response) is dict:
            self.username = response['username']
            self.password = response['password']
    
    def get_cookies(self, driver):
        response = self.service.get_cookies(self.username)
        if type(response) is dict:
            load_cookies(driver, response['cookies'])
    
    def save_cookies(self, driver):
        save_cookies(self.username, self.service, driver)
    
    def get_useragent(self, options):
        response = self.service.get_useragent(self.username)
        if type(response) is dict:
            load_useragent(options, response['useragent'])
    
    def save_useragent(self, driver):
        save_useragent(self.username, self.service, driver)

    def get_question(self):
        question = self.service.get_question(self.username)
