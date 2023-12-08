from bot import NaverKinBot
from seleniumbase import Driver, undetected
from utils import short_sleep, long_sleep, bring_browser_to_front, check_answer_registered
import pyperclip
import pyautogui
from networking.service import send_notification, update_account_interactions, save_answer_response, get_answer_response
import asyncio
from datetime import datetime

class AnswerBot(NaverKinBot):
    def __init__(self, queues, mode: int) -> None:
        super().__init__(queues)
        self.mode = mode

    async def main(self):
        if not await super().main():
            self.running = False
            return
        answer = await self.data_queue.get()
        print(answer)
        # WAIT FOR QUESTIONBOT TO SEND THE QUESTION LINK
        question = await self.data_queue.get()
        print(question)

        if await self.answer_question(self.driver, question, answer):
            await update_account_interactions(question["question_bot_username"], self.account["username"])
            await self.send_notification_after_answering(question)

        self.running = False
        return

    async def answer_question(self, driver: undetected.Chrome, question: dict, answer: str) -> bool:
        try:
            await short_sleep(5)
            question_link = question["question_link"] + '&mode=answer'
            driver.uc_open_with_reconnect(question_link, 10)
            await bring_browser_to_front()
            pyautogui.press('esc')
            pyautogui.press('home')
            await short_sleep(30)
            answer_content = ""
            if self.mode == 0:
                answer_content = answer["answer_advertisement"]
                answer_type = "answer_advertisement"
            elif self.mode == 1:
                answer_content = answer["answer_exposure"]
                answer_type = "answer_exposure"
            pyperclip.copy(answer_content)
            await bring_browser_to_front()
            pyautogui.press('home')
            pyautogui.hotkey('ctrl', 'v')
            await long_sleep(self.configs["submit_delay"])
            try:
                driver.execute_script("document.querySelector('#answerRegisterButton').click()")
                await self.handle_alerts(driver=driver)
            except:
                print("can not click answer submit")

            await short_sleep(10)
            account_url = self.account["account_url"].split("naver.com")[-1]
            if await check_answer_registered(driver=self.driver, question_link=question_link, account_url=account_url, handle_alerts=self.handle_alerts):
                await save_answer_response(question_url=question_link, type=answer_type, content=answer_content, username=self.account["username"], postscript="", date_answered=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                save_attempts = 0
                while True:
                    if save_attempts >= 3:
                        print("ERROR SAVING ANSWER RESPONSE TO DATABASE")
                        break
                    await asyncio.sleep(5)
                    await get_answer_response(filters={"question_url": question_link, "username": self.account["username"], "type": answer_type})
                    saved_answer_response = await self.data_queue.get()
                    if saved_answer_response["question_url"] == question_link and saved_answer_response["username"] == self.account["username"] and saved_answer_response["type"] == answer_type:
                        print("SAVED ANSWER RESPONSE TO DATABASE")
                        break
                    else:
                        await save_answer_response(question_url=question_link, type=answer_type, content=answer_content, username=self.account["username"], postscript="", date_answered=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        save_attempts += 1
                return True
            else:
                print("ANSWER IS NOT REGISTERED")
                return self.answer_question(driver=driver, question=question, answer=answer)
        except Exception as e:
            print("THERE IS ERROR WHILE ANSWERING")
            print(e)
            return False
    
    async def send_notification_after_answering(self, question):
        await short_sleep(5)
        data = {}
        data['question_link'] = question['question_link']
        data['question_bot_username'] = question['question_bot_username']
        if self.mode == 0:
            # FROM ANSWERBOT_ADVERTISEMENT TO QUESTIONBOT FOR ANSWER SELECTION
            data['respondent_url'] = self.account['account_url']
            await send_notification(send_to="questionbot", data=data)
            print("SENT NOTIFICATION TO QUESTIONBOT FOR ANSWER SELECTION")
        elif self.mode == 1:
            # FROM ANSWERBOT_EXPOSURE TO ANSWERBOT_ADVERTISEMENT
            await send_notification(send_to="answerbot_advertisement", data=data)
            print("SENT NOTIFICATION TO ANSWERBOT_ADVERTISEMENT")