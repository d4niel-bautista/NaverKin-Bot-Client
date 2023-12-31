from bot import NaverKinBot
from seleniumbase import Driver, undetected
from utils import short_sleep, long_sleep, bring_browser_to_front
import pyperclip
import pyautogui
from networking.service import send_notification, save_question_post
from datetime import datetime

class QuestionBot(NaverKinBot):
    def __init__(self, queues) -> None:
        super().__init__(queues)
    
    async def main(self):
        if not await super().main():
            self.running = False
            return
        question = await self.data_queue.get()
        print(question)

        self.mode = await self.data_queue.get()
        print(f"MODE: {self.mode}")
        if not self.mode or (self.mode != "1Q1A" and self.mode != "1Q2A"):
            print(f'HAS RECEIVED NO MODE OR IMPROPER MODE: "{self.mode}". STOPPING PROGRAM')
            self.running = False
            return

        post_attempts = 0
        while True:
            if post_attempts >= 3:
                print("ERROR WITH WRITING QUESTION")
                return False
            await self.write_question(self.driver, question['question'])
            if "qna/detail.naver" in self.driver.current_url:
                break
            post_attempts += 1
            print("RETRYING TO WRITE QUESTION")

        await save_question_post(question_url=self.driver.current_url, title=question['question']['title'], author=self.account['username'], respondent="", date_posted=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        await short_sleep(5)
        await self.send_question_link(self.driver)
        # WAIT FOR ANSWERBOT_ADVERTISEMENT ANSWER NOTIFICATION
        answer_selection = await self.data_queue.get()
        print(answer_selection)

        await self.select_answer(self.driver, answer_selection)
        self.running = False
        return
    
    async def write_question(self, driver: undetected.Chrome, question: dict):
        print("WILL START WRITING A QUESTION")
        await short_sleep(5)
        driver.uc_open_with_reconnect('https://kin.naver.com/qna/question.naver', 10)
        await self.handle_alerts(self.driver)
        await self.close_popups(self.driver)
        await short_sleep(10)
        pyperclip.copy(question['title'])
        await bring_browser_to_front()
        pyautogui.hotkey('ctrl', 'v')
        await short_sleep(5)
        editor_iframe = driver.find_element('xpath', '//iframe[@id="editor"]')
        driver.switch_to.frame(editor_iframe)
        await short_sleep(5)
        smart_editor_iframe = driver.find_element('xpath', '//iframe[@id="SmartEditorIframe"]')
        driver.switch_to.frame(smart_editor_iframe)
        await short_sleep(5)
        pyperclip.copy(question['content'])
        driver.click('xpath', '/html/body')
        await short_sleep(10)
        await bring_browser_to_front()
        pyautogui.hotkey('ctrl', 'v')
        await short_sleep(10)
        driver.switch_to.parent_frame()
        driver.click('xpath', '//button[@class="button_style is_primary _register"]')
        await long_sleep(self.configs['submit_delay'])
        driver.execute_script("""document.getElementsByClassName("button_style is_primary _register _clickcode:sbm.ok")[0].click()""")
        await short_sleep(10)
        driver.switch_to.alert.accept()
        await short_sleep(5)
        
    async def send_question_link(self, driver: undetected.Chrome):
        await short_sleep(5)
        question_url = driver.current_url
        if self.mode == "1Q1A":
            await send_notification(send_to="answerbot_advertisement", data={"question_link": question_url, "question_bot_username": self.account["username"]})
            print("SENT QUESTION LINK NOTIFICATION TO ANSWERBOT_ADVERTISEMENT")
        elif self.mode == "1Q2A":
            await send_notification(send_to="answerbot_exposure", data={"question_link": question_url, "question_bot_username": self.account["username"]})
            print("SENT QUESTION LINK NOTIFICATION TO ANSWERBOT_EXPOSURE")

    async def select_answer(self, driver: undetected.Chrome, answer_selection: dict):
        await short_sleep(5)
        driver.uc_open_with_reconnect(answer_selection['question_link'], 10)
        await short_sleep(10)
        answers = driver.find_elements('xpath', '//div[@class="answer-content__item _contentWrap _answer"]')
        for answer in answers:
            answer_id = answer.get_attribute('id')
            respondent = answer.find_elements('xpath', f'//div[@id="{answer_id}"]//div[@class="profile_card"]//div[@class="profile_info"]/a[@class="name_area"]')
            if respondent:
                if not respondent[0].get_attribute('href') == answer_selection['respondent_url']:
                    continue
                respondent_name = respondent[0].find_element('xpath', './strong[@class="name"]').text
                select_answer = answer.find_element('xpath', f'//div[@id="{answer_id}"]//div[@class="c-userinfo-answer _answerBottom"]//div[@class="c-userinfo-answer__right"]/a[@class="_answerSelectArea button_compose"]')
                select_answer.click()
                print(f"SELECTED {respondent_name}'s ANSWER")