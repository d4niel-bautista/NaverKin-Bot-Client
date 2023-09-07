from networking.service import Service
from crawler.session_manager import save_cookies, load_cookies, load_useragent, save_useragent
import undetected_chromedriver as uc
import subprocess
import time
import pyautogui
import pyperclip
from .chatgpt import generate_response, generate_question

class Crawler():
    username = ''
    password = ''
    role = ''
    submit_delay = 60
    page_refresh = 300
    cooldown = 3600
    prohibited_words = []
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
            self.role = response['role']
            return True
        return False

    def get_configs(self):
        response = self.service.get_configs(self.role)
        if type(response) is dict:
            self.submit_delay = response['submit_delay']
            self.page_refresh = response['page_refresh']
            self.cooldown = response['cooldown']
            self.prohibited_words = response['prohibited_words']
    
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

    def get_question(self):
        question = self.service.get_question(self.username)
        return question['id']
    
    def save_question(self, driver: uc.Chrome, title):
        id = driver.current_url
        print(self.service.save_question(id, title, self.username))
        
    def init_driver(self):
        try:
            subprocess.call('taskkill /f /im chrome.exe /t')
        except:
            pass

        options = uc.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-notifications')
        prefs = {"credentials_enable_service": False,
                "profile.password_manager_enabled": False}
        options.add_experimental_option("prefs", prefs)

        driver = uc.Chrome(options=options, use_subprocess=True)
        return driver
    
    def start(self):
        if self.get_account():
            self.get_configs()
            driver = self.init_driver()
            if self.get_cookies(driver=driver):
                if not self.get_useragent(driver.options):
                    self.save_useragent(driver)
                    time.sleep(5)
                    self.get_useragent(driver.options)
                self.main(driver)
            else:
                self.first_run(driver)
                self.main(driver)
        else:
            time.sleep(10)
            return self.start()
        return self.service.disconnect(self.username)
                
    def main(self, driver):
        driver.get('https://kin.naver.com')
        pyautogui.press('esc')
        time.sleep(5)
        if self.role == 0:
            self.respondent_loop(driver)
        elif self.role == 1:
            self.questioner_loop(driver)

    def first_run(self, driver):
        driver.get(r'https://nid.naver.com/nidlogin.login?url=https%3A%2F%2Fkin.naver.com%2F')
        pyautogui.press('esc')
        self.login(driver)
        time.sleep(5)
        self.save_cookies(driver)
        self.save_useragent(driver)

    def login(self, driver):
        time.sleep(5)
        pyautogui.press('esc')
        pyperclip.copy(self.username)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(5)
        pyautogui.press('tab')
        time.sleep(5)
        pyperclip.copy(self.password)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(5)
        login_btn = driver.find_element('xpath', '//*[@id="log.login"]')
        login_btn.click()
    
    def questioner_loop(self, driver):
        while True:
            driver.get('https://kin.naver.com/qna/question.naver')
            pyautogui.press('esc')
            time.sleep(10)
            title = self.write_question(driver)
            self.save_question(driver, title)
            time.sleep(self.page_refresh)
    
    def write_question(self, driver: uc.Chrome):
        title, content = generate_question()
        time.sleep(10)
        pyperclip.copy(title)
        pyautogui.hotkey('ctrl', 'v')
        editor_iframe = driver.find_element('xpath', '//iframe[@id="editor"]')
        driver.switch_to.frame(editor_iframe)
        time.sleep(5)
        smart_editor_iframe = driver.find_element('xpath', '//iframe[@id="SmartEditorIframe"]')
        driver.switch_to.frame(smart_editor_iframe)
        time.sleep(5)
        pyperclip.copy(content)
        body_content = driver.find_element('xpath', '/html/body')
        body_content.click()
        time.sleep(10)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(10)
        driver.switch_to.parent_frame()
        submit_btn = driver.find_elements('xpath', '//button[contains(@class, "button_style is_primary _register")]')[0]
        submit_btn.click()
        time.sleep(self.submit_delay)
        submit_btn = driver.find_elements('xpath', '//button[contains(@class, "button_style is_primary _register")]')[1]
        submit_btn.click()
        time.sleep(10)
        driver.switch_to.alert.accept()
        time.sleep(5)
        return title

    def respondent_loop(self, driver):
        pass