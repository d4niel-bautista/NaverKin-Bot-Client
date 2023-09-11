from networking.service import Service
from crawler.session_manager import save_cookies, load_cookies, load_useragent, save_useragent, logged_in
import undetected_chromedriver as uc
import subprocess
import time
import pyautogui
import pyperclip
from .chatgpt import generate_response, generate_question
from utils import bring_browser_to_front, clean_question_content, pad_prescript_postscript
from bs4 import BeautifulSoup
from crawler.validators import text_has_prohibited_words
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    
    def update_account_status(self, status):
        response = self.service.update_account(self.username, status)
        print(response)

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
        question = self.service.get_question(self.username, self.role)
        if type(question) is dict:
            return question
        return False
    
    def save_question(self, driver: uc.Chrome, title):
        id = driver.current_url
        print(self.service.save_question(id, title, self.username))
    
    def update_question_status_after_answer_selection(self, question_id):
        self.service.update_question(question_id=question_id, author=self.username, status=2)
        
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
                
    def main(self, driver):
        driver.get('https://kin.naver.com')
        bring_browser_to_front()
        pyautogui.press('esc')
        time.sleep(5)
        if self.role == 0:
            self.respondent_loop(driver)
        elif self.role == 1:
            self.questioner_loop(driver)

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
    
    def questioner_loop(self, driver):
        while True:
            driver.get('https://kin.naver.com/qna/question.naver')
            if not self.close_popups(driver):
                self.select_answer(driver)
                continue
            pyautogui.press('esc')
            time.sleep(10)
            title = self.write_question(driver)
            self.save_question(driver, title)
            time.sleep(self.page_refresh)
    
    def write_question(self, driver: uc.Chrome):
        title, content = generate_question()
        time.sleep(10)
        pyperclip.copy(title)
        bring_browser_to_front()
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
        bring_browser_to_front()
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

    def respondent_loop(self, driver: uc.Chrome):
        while True:
            question = self.get_question()
            if not question:
                time.sleep(self.page_refresh)
                continue
            driver.get(question['id'])
            time.sleep(2)
            bring_browser_to_front()
            pyautogui.press('home')
            self.answer_question(driver)
    
    def answer_question(self, driver: uc.Chrome):
        time.sleep(5)
        driver.find_element('xpath', '//div[contains(@class, "c-heading _questionContentsArea")]')
        soup = BeautifulSoup(driver.page_source, 'lxml')
        question_content = soup.select_one('div.c-heading._questionContentsArea')
        question_content_cleaned = clean_question_content(question_content)
        while True:
            response = generate_response(question_content_cleaned)
            if not text_has_prohibited_words(self.prohibited_words, response):
                break
            time.sleep(10)
        finalized_text = pad_prescript_postscript(response)
        bring_browser_to_front()
        pyautogui.press('home')
        pyperclip.copy(finalized_text)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(self.submit_delay)
        register_answer_btn = driver.find_element('xpath', '//div[@id="smartEditorArea"]//div[@id="answerButtonArea"]//a[@id="answerRegisterButton"]')
        driver.execute_script('arguments[0].click();', register_answer_btn)
        self.handle_alerts(driver)
        time.sleep(self.page_refresh)

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
    
    def select_answer(self, driver: uc.Chrome):
        time.sleep(5)
        question = self.get_question()
        if not question:
            time.sleep(self.page_refresh)
            return
        driver.get(question['id'])
        time.sleep(10)
        answers = driver.find_elements('xpath', '//div[@class="answer-content__item _contentWrap _answer"]')
        for answer in answers:
            answer_id = answer.get_attribute('id')
            respondent = answer.find_elements('xpath', f'//div[@id="{answer_id}"]//div[@class="profile_card"]//div[@class="profile_info"]/a[@class="name_area"]')
            if respondent:
                if not respondent[0].get_attribute('href') == question['respondent_url']:
                    continue
                select_answer = answer.find_element('xpath', f'//div[@id="{answer_id}"]//div[@class="c-userinfo-answer _answerBottom"]//div[@class="c-userinfo-answer__right"]/a[@class="_answerSelectArea button_compose"]')
                select_answer.click()
                print(f"SELECTED {question['respondent']} RESPONDENT'S ANSWER")
                self.update_question_status_after_answer_selection(question['id'])
        time.sleep(10)
        self.close_popups(driver)
        time.sleep(self.cooldown)
