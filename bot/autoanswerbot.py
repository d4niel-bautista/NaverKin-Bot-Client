from bot import NaverKinBot
from seleniumbase import Driver, undetected
from utils import short_sleep, long_sleep, bring_browser_to_front, text_has_links, has_prohibited_words, clean_question_content, generate_text, check_answer_registered
import asyncio
from bs4 import BeautifulSoup
import pyperclip
import pyautogui
from datetime import datetime
from networking.service import save_answer_response, get_answer_response

class AutoanswerBot(NaverKinBot):
    def __init__(self, queues) -> None:
        self.answers_count = 0
        self.reached_id_limit = False
        super().__init__(queues)

    async def main(self):
        if not await super().main():
            self.running = False
            return
        self.prompt_configs = await self.data_queue.get()
        print(self.prompt_configs)
        await short_sleep(5)
        while self.stop == False:
            if self.reached_id_limit or self.answers_count >= self.configs["answers_per_day"]:
                print(f"IN COOLDOWN\nID LIMIT: {self.reached_id_limit}\nANSWER COUNT: {self.answers_count}/{self.configs['answers_per_day']}")
                await long_sleep(self.configs["cooldown"])
                self.reached_id_limit = False
                self.answers_count = 0
            if self.stop:
                break
            question_link = await self.get_first_question(self.driver)
            if await self.write_answer(driver=self.driver, question_link=question_link):
                self.answers_count += 1
            print(f"ANSWERED {self.answers_count}/{self.configs['answers_per_day']}")
            await long_sleep(self.configs["page_refresh"])
        print("STOPPING PROGRAM")
        self.running = False
        return
    
    async def get_first_question(self, driver: undetected.Chrome):
        driver.uc_open_with_reconnect('https://kin.naver.com/', 10)
        await self.handle_alerts(driver=driver)
        await asyncio.sleep(2)
        self.driver.execute_script("""document.querySelector("li._onlyTitle a[class^='type_title _onlyTitleTypeBtn']").click()""")
        await asyncio.sleep(1)
        self.driver.execute_script("""document.querySelector("li._recent a._sort_option").click()""")
        await asyncio.sleep(1)
        first_question = driver.find_element('xpath', '//div[@id="questionListTypeTitle"]/div[1]')
        soup = BeautifulSoup(first_question.get_attribute('outerHTML'), 'lxml').find('div', class_ = 'answer_box')
        if len(soup.find_all('span', {'class': 'ico_picture sp_common'})) + len(soup.find_all('span', {'class': 'ico_file sp_common'})) + int(soup.find('span', {'class': 'num_answer'}).find('em').text) == 0:
            if not await has_prohibited_words(text=soup.find('span', {'class': 'tit_txt'}).text, prohibited_words=self.prompt_configs['prohibited_words']):
                link = soup.find('a', {'class': '_first_focusable_link'})['href'].strip()
                if link:
                    print(f"GOT VALID QUESTION {link}")
                    return link
        print("NO VALID QUESTION")
        await long_sleep(120)
        return await self.get_first_question(driver=driver)
    
    async def write_answer(self, driver: undetected.Chrome, question_link: str):
        print("STARTS ANSWERING")
        question_link = 'https://kin.naver.com' + question_link
        driver.uc_open_with_reconnect(question_link, 10)
        await asyncio.sleep(1)
        await self.handle_alerts(driver=driver)
        await self.close_popups(driver=driver)
        await asyncio.sleep(5)
        await bring_browser_to_front()
        pyautogui.press('esc')
        await short_sleep(10)
        question_content = driver.find_element('xpath', '//*[@id="content"]/div[1]/div/div[1]')
        soup = BeautifulSoup(question_content.get_attribute('outerHTML'), 'lxml')

        video_content = soup.find('div', {'class': 'kin_movie_info'})
        link_content = soup.find('a')
        image_content = soup.find('img')
        if video_content:
            print('SKIPPED! HAS VIDEO CONTENT' + '\n')
            return False
        elif link_content:
            print('SKIPPED! HAS DETECTED LINK' + '\n')
            return False
        elif image_content:
            print('SKIPPED! HAS DETECTED IMAGE' + '\n')
            return False
        soup_cleaned = await clean_question_content(tag=soup)
        if await text_has_links(soup_cleaned) or await has_prohibited_words(text=soup_cleaned, prohibited_words=self.prompt_configs['prohibited_words']) or self.reached_id_limit:
            return False
        
        response = await generate_text(query=soup_cleaned, prompt=self.prompt_configs['prompt'], prohibited_words=self.prompt_configs['prohibited_words'], prescript=self.prompt_configs['prescript'], postscript=self.prompt_configs['postscript'])

        if response == "ERROR WITH CHATGPT" or response == "CHATGPT ERROR: KEEPS DETECTING PROHIBITED WORDS IN RESPONSE":
            print(response)
            return False
        pyperclip.copy(response)
        await asyncio.sleep(1)
        await bring_browser_to_front()
        pyautogui.press('home')
        try:
            driver.uc_click(selector='//*[@id="smartEditor"]/div/div/div/div[1]/div/section/article', by="xpath")
        except:
            print("can't click article element")
        pyautogui.hotkey('ctrl', 'v')
        await long_sleep(self.configs['submit_delay'])
        if self.reached_id_limit or self.stop:
            return False
        try:
            driver.execute_script("document.querySelector('#answerRegisterButton').click()")
            await self.handle_alerts(driver=driver)
        except:
            print("can not click answer submit")
        await short_sleep(5)
        await self.close_popups(driver=driver)
        await short_sleep(10)
        account_url = self.account["account_url"].split("naver.com")[-1]
        if await check_answer_registered(driver=self.driver, question_link=question_link, account_url=account_url, handle_alerts=self.handle_alerts):
            await save_answer_response(question_url=question_link, type="autoanswer", content=response, username=self.account["username"], postscript=self.prompt_configs['postscript'], date_answered=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            save_attempts = 0
            while True:
                if save_attempts >= 3:
                    print("ERROR SAVING ANSWER RESPONSE TO DATABASE")
                    return False
                await asyncio.sleep(5)
                await get_answer_response(filters={"question_url": question_link, "username": self.account["username"], "type": "autoanswer"})
                saved_answer_response = await self.data_queue.get()
                if saved_answer_response["question_url"] == question_link and saved_answer_response["username"] == self.account["username"] and saved_answer_response["type"] == "autoanswer":
                    print("SAVED ANSWER RESPONSE TO DATABASE")
                    return True
                else:
                    await save_answer_response(question_url=question_link, type="autoanswer", content=response, username=self.account["username"], postscript=self.prompt_configs['postscript'], date_answered=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    save_attempts += 1
        else:
            print("ANSWER IS NOT REGISTERED")
            return False