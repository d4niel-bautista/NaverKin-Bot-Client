from bot import NaverKinBot
import undetected_chromedriver as uc
from utils import short_sleep, long_sleep, bring_browser_to_front
import pyperclip
import pyautogui
from networking.service import send_notification

class AnswerBot(NaverKinBot):
    def __init__(self, queues, mode: int) -> None:
        super().__init__(queues)
        self.mode = mode

    async def main(self):
        await super().main()
        answer = await self.data_queue.get()
        print(answer)
        # WAIT FOR QUESTIONBOT TO SEND THE QUESTION LINK
        question = await self.data_queue.get()
        print(question)
        if await self.answer_question(self.driver, question, answer):
            await self.send_notification_after_answering(question)
        self.running = False
        return

    async def answer_question(self, driver: uc.Chrome, question: dict, answer: str) -> bool:
        try:
            await short_sleep(5)
            driver.get(question["question_link"] + '&mode=answer')
            await bring_browser_to_front()
            pyautogui.press('esc')
            pyautogui.press('home')
            await short_sleep(30)
            if self.mode == 0:
                pyperclip.copy(answer["answer_advertisement"])
            elif self.mode == 1:
                pyperclip.copy(answer["answer_exposure"])
            await bring_browser_to_front()
            pyautogui.press('home')
            pyautogui.hotkey('ctrl', 'v')
            # await long_sleep(self.configs["submit_delay"])
            # register_answer_btn = driver.find_element('xpath', '//div[@id="smartEditorArea"]//div[@id="answerButtonArea"]//a[@id="answerRegisterButton"]')
            # driver.execute_script('arguments[0].click();', register_answer_btn)
            return True
        except Exception as e:
            print(e)
            return False
    
    async def send_notification_after_answering(self, question):
        await short_sleep(5)
        data = {}
        data['question_link'] = question['question_link']
        if self.mode == 0:
            # FROM ANSWERBOT_ADVERTISEMENT TO QUESTIONBOT FOR ANSWER SELECTION
            data['respondent_url'] = self.account['account_url']
            await send_notification(send_to="QuestionBot", data=data)
            print("SENT NOTIFICATION TO QUESTIONBOT FOR ANSWER SELECTION")
        elif self.mode == 1:
            # FROM ANSWERBOT_EXPOSURE TO ANSWERBOT_ADVERTISEMENT
            await send_notification(send_to="AnswerBot_Advertisement", data=data)
            print("SENT NOTIFICATION TO ANSWERBOT_ADVERTISEMENT")