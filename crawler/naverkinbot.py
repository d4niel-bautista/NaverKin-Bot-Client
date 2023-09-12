import undetected_chromedriver as uc
import subprocess
import time
import pyautogui
import pyperclip
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from crawler.session_manager import save_cookies, load_cookies, load_useragent, save_useragent, logged_in
from utils import bring_browser_to_front
from networking.service import Service

class NaverKinBot():
    def __init__(self, service: Service):
        self.service = service
    
    def get_account(self):
        response = self.service.get_account()
        if type(response) is dict:
            self.username = response['username']
            self.password = response['password']
            self.levelup_id = response['levelup_id']
            return True
        return False
    
    def release_account(self):
        response = self.update_account_status(self.username, 0)
        print(response)
        self.username = ''
        self.password = ''
        self.levelup_id = ''
        time.sleep(10)
    
    def update_account_status(self, status):
        response = self.service.update_account(self.username, status)
        print(response)
    
    def get_question(self, role):
        question = self.service.get_question(self.username, role, self.levelup_id)
        if type(question) is dict:
            return question
        return False
    
    def get_configs(self):
        response = self.service.get_configs(self.role)
        if type(response) is dict:
            self.submit_delay = response['submit_delay']
            self.page_refresh = response['page_refresh']
            self.cooldown = response['cooldown']
            self.prohibited_words = [i.rstrip() for i in response['prohibited_words'].split('\n')]
    
    def get_cookies(self, driver):
        response = self.service.get_cookies(self.username)
        if type(response) is dict:
            load_cookies(driver, response['cookies'])
            return True
        return False
    
    def save_cookies(self, driver):
        save_cookies(self.username, self.service, driver)
    
    def get_useragent(self, options):
        response = self.service.get_useragent(self.username)
        if type(response) is dict:
            load_useragent(options, response['useragent'])
            return True
        return False
    
    def save_useragent(self, driver):
        save_useragent(self.username, self.service, driver)
        
    def init_driver(self):
        try:
            subprocess.call('taskkill /f /im chrome.exe /t')
        except:
            pass

        options = uc.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-notifications')
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-popup-blocking")
        prefs = {"credentials_enable_service": False,
                "profile.password_manager_enabled": False}
        options.add_experimental_option("prefs", prefs)

        driver = uc.Chrome(options=options, use_subprocess=True)
        driver.maximize_window()
        return driver
        
    def start(self):
        if self.get_account():
            self.get_configs()
            driver = self.init_driver()
            driver.get('https://naver.com')
            time.sleep(10)
            if not self.get_cookies(driver=driver):
                self.login(driver)
            if not logged_in(driver):
                self.login(driver)
            if not self.get_useragent(driver.options):
                self.save_useragent(driver)
                time.sleep(5)
                self.get_useragent(driver.options)
            self.main(driver)
        else:
            time.sleep(10)
            return self.start()
        return self.service.disconnect(self.username)
    
    def main(self, driver: uc.Chrome):
        driver.get('https://kin.naver.com')
        bring_browser_to_front()
        pyautogui.press('esc')
        time.sleep(5)
    
    def login(self, driver):
        driver.get(r'https://nid.naver.com/nidlogin.login?url=https%3A%2F%2Fkin.naver.com%2F')
        bring_browser_to_front()
        pyautogui.press('esc')
        self.authenticate(driver)
        time.sleep(5)
        self.save_cookies(driver)
        self.save_useragent(driver)

    def authenticate(self, driver: uc.Chrome):
        time.sleep(5)
        pyautogui.press('esc')
        pyperclip.copy(self.username)
        bring_browser_to_front()
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(5)
        bring_browser_to_front()
        pyautogui.press('tab')
        time.sleep(5)
        pyperclip.copy(self.password)
        bring_browser_to_front()
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(5)
        login_btn = driver.find_element('xpath', '//*[@id="log.login"]')
        login_btn.click()
    
    def handle_alerts(self, driver: uc.Chrome):
        try:
            WebDriverWait(driver, 3).until (EC.alert_is_present())
            alert = driver.switch_to.alert
            if "등급에서 하루에 등록할 수 있는 답변 개수는" in alert.text:
                alert.accept()
                print(f"{self.username} HAS REACHED ID LIMIT")
                self.update_account_status(2)
                time.sleep(self.cooldown)
                return self.start()
            else:
                alert.accept()
        except:
            print('No alert detected')

    def close_popups(self, driver: uc.Chrome):
        time.sleep(5)
        try:
            popups = driver.find_elements('xpath', '//div[contains(@class, "section_layer")]')
            for popup in popups:
                if popup.is_displayed():
                    popup_id = popup.get_attribute('id')
                    a_close = driver.find_elements('xpath', f'//div[@id="{popup_id}"]//a[@href="#" or contains(@class, "close")]')
                    btn_close = driver.find_elements('xpath', f'//div[@id="{popup_id}"]//button[@type="button" and contains(@class, "close")]')
                    if a_close:
                        driver.execute_script('arguments[0].click();', a_close[0])
                    elif btn_close:
                        btn_close[0].click()
                    else:
                        print('Popup has no detected close button element')
                        return False
            return True
        except:
            print("No popup or popup can't be closed")
            return False