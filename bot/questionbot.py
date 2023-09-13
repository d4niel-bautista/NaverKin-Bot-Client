import undetected_chromedriver as uc
from bot.naverkinbot import NaverKinBot
import time
import pyautogui
import pyperclip
from bot.chatgpt import generate_question
from utils import bring_browser_to_front
from bot.validators import text_has_prohibited_words

class QuestionBot(NaverKinBot):
    def __init__(self, service):
        super().__init__(service)
        self.role = 1
    
    def save_question(self, driver: uc.Chrome, title):
        id = driver.current_url
        print(self.service.save_question(id, title, self.username))
    
    def update_question_status_after_answer_selection(self, question_id):
        self.service.update_question(question_id=question_id, author=self.username, status=3)
    
    def main(self, driver: uc.Chrome):
        while True:
            driver.get('https://kin.naver.com/qna/question.naver')
            if not self.close_popups(driver):
                self.select_answer(driver)
                continue
            pyautogui.press('esc')
            time.sleep(10)
            title = self.write_question(driver)
            self.save_question(driver, title)
            self.close_popups(driver)
            time.sleep(self.page_refresh)
            self.select_answer(driver)
            time.sleep(self.cooldown)
    
    def write_question(self, driver: uc.Chrome):
        while True:
            title, content = generate_question()
            if not text_has_prohibited_words(self.prohibited_words, title + " " + content):
                break
            time.sleep(15)
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

    def select_answer(self, driver: uc.Chrome):
        time.sleep(5)
        question = self.get_question(self.role)
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