from bot import NaverKinBot
import undetected_chromedriver as uc
from utils import short_sleep, long_sleep, bring_browser_to_front
import pyperclip
import pyautogui
from networking.service import send_notification

class QuestionBot(NaverKinBot):
    def __init__(self, queues) -> None:
        super().__init__(queues)
    
    async def main(self):
        await super().main()
        question = await self.data_queue.get()
        print(question)
        await self.write_question(self.driver, question['question'])
        await self.send_question_link(self.driver)
        answer_selection = await self.data_queue.get()
        print(answer_selection)
        await self.select_answer(self.driver, answer_selection)
        self.running = False
        return
    
    async def write_question(self, driver: uc.Chrome, question: dict):
        print("WILL START WRITING A QUESTION")
        await short_sleep(5)
        driver.get('https://kin.naver.com/qna/question.naver')
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
        body_content = driver.find_element('xpath', '/html/body')
        body_content.click()
        await short_sleep(10)
        await bring_browser_to_front()
        pyautogui.hotkey('ctrl', 'v')
        await short_sleep(10)
        driver.switch_to.parent_frame()
        submit_btn = driver.find_elements('xpath', '//button[contains(@class, "button_style is_primary _register")]')[0]
        submit_btn.click()
        # await long_sleep(self.configs['submit_delay'])
        # submit_btn = driver.find_elements('xpath', '//button[contains(@class, "button_style is_primary _register")]')[1]
        # submit_btn.click()
        # await short_sleep(10)
        # driver.switch_to.alert.accept()
        # await short_sleep(5)
        
    async def send_question_link(self, driver: uc.Chrome):
        await short_sleep(5)
        question_url = driver.current_url
        await send_notification(send_to="AnswerBot_Exposure", data={"question_link": question_url})
        print("SENT QUESTION LINK NOTIFICATION TO AnswerBot_Exposure")

    async def select_answer(self, driver: uc.Chrome, answer_selection: dict):
        await short_sleep(5)
        driver.get(answer_selection['question_link'])
        # driver.switch_to.alert.accept()
        await short_sleep(10)
        answers = driver.find_elements('xpath', '//div[@class="answer-content__item _contentWrap _answer"]')
        print(answers)
        for answer in answers:
            answer_id = answer.get_attribute('id')
            respondent = answer.find_elements('xpath', f'//div[@id="{answer_id}"]//div[@class="profile_card"]//div[@class="profile_info"]/a[@class="name_area"]')
            print(respondent[0])
            if respondent:
                print(respondent[0].get_attribute('href'), answer_selection['respondent_url'])
                if not respondent[0].get_attribute('href') == answer_selection['respondent_url']:
                    continue
                respondent_name = respondent[0].find_element('xpath', '//strong[@class="name"]').text
                # select_answer = answer.find_element('xpath', f'//div[@id="{answer_id}"]//div[@class="c-userinfo-answer _answerBottom"]//div[@class="c-userinfo-answer__right"]/a[@class="_answerSelectArea button_compose"]')
                # select_answer.click()
                print(f"SELECTED {respondent_name}'s ANSWER")