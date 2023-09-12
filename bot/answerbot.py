import undetected_chromedriver as uc
from bot.naverkinbot import NaverKinBot
from networking.service import Service
import time
import pyautogui
import pyperclip
from .chatgpt import generate_response
from utils import bring_browser_to_front, clean_question_content, pad_prescript_postscript
from bs4 import BeautifulSoup
from bot.validators import text_has_prohibited_words

class AnswerBot(NaverKinBot):
    def __init__(self, service: Service):
        super().__init__(service)
        self.role = 0
    
    def update_question_status_after_answering(self, question_id):
        if self.levelup_id:
            self.service.update_question(question_id=question_id, respondent=self.username, status=2)
        else:
            self.service.update_question(question_id=question_id, respondent=self.username, status=1)
    
    def main(self, driver: uc.Chrome):
        while True:
            question = self.get_question(self.role)
            if not question:
                time.sleep(self.page_refresh)
                continue
            driver.get(question['id'] + '&mode=answer')
            time.sleep(5)
            smart_editor_area = driver.find_element('xpath', '//div[@id="smartEditorArea"]')
            if not smart_editor_area.is_displayed():
                print(f"QUESTION {question['id']} ALREADY HAS SELECTED ANSWER")
                time.sleep(self.page_refresh)
                continue
            bring_browser_to_front()
            pyautogui.press('home')
            self.answer_question(driver)
            self.update_question_status_after_answering(question['id'])
            time.sleep(self.page_refresh)
    
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