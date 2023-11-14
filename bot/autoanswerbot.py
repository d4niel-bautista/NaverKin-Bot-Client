from bot import NaverKinBot
import undetected_chromedriver as uc
from utils import short_sleep, long_sleep, bring_browser_to_front, text_has_links, has_prohibited_words, clean_question_content
import asyncio
from bs4 import BeautifulSoup

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
        self.driver.execute_script("""document.querySelector("li._onlyTitle a[class^='type_title _onlyTitleTypeBtn']").click()""")
        question_link = await self.get_first_question(self.driver)
        if not self.stop:
            await self.write_answer(driver=self.driver, question_link=question_link)
        while self.answers_count < self.configs["answers_per_day"] and self.stop == False:
            pass
    
    async def get_first_question(self, driver: uc.Chrome):
        driver.get('https://kin.naver.com/')
        await asyncio.sleep(1)
        first_question = driver.find_element('xpath', '//div[@id="questionListTypeTitle"]/div[1]')
        soup = BeautifulSoup(first_question.get_attribute('outerHTML'), 'lxml').find('div', class_ = 'answer_box')
        if len(soup.find_all('span', {'class': 'ico_picture sp_common'})) + len(soup.find_all('span', {'class': 'ico_file sp_common'})) + int(soup.find('span', {'class': 'num_answer'}).find('em').text) == 0:
            if not await has_prohibited_words(text=soup.find('span', {'class': 'tit_txt'}).text, prohibited_words=self.prompt_configs['prohibited_words']):
                link = soup.find('a', {'class': '_first_focusable_link'})['href'].strip()
                if link:
                    print("GOT VALID QUESTION LINK")
                    return link
        return await self.get_first_question(driver=driver)
    
    async def write_answer(self, driver: uc.Chrome, question_link: str):
        print("STARTS ANSWERING")
        driver.get('https://kin.naver.com' + question_link)
        await asyncio.sleep(1)
    
    async def handle_alerts(self, driver: uc.Chrome):
        try:
            alert = driver.switch_to.alert
            if "등급에서 하루에 등록할 수 있는 답변 개수는" in alert.text:
                self.reached_id_limit = True
                self.stop = True
                alert.accept()
            else:
                alert.accept()
        except:
            pass