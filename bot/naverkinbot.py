from .async_worker import AsyncWorker
import asyncio
import subprocess
from seleniumbase import Driver, undetected
from utils import get_chrome_browser_version, reconnect_modem, bring_browser_to_front, short_sleep, get_current_public_ip
from .session_manager import load_useragent, load_cookies, logged_in, save_cookies, save_user_agent
import pyautogui
import pyperclip
from networking.service import send_logging_data, send_update_request, save_login, websocket_connect, websocket_disconnect, update_state, get_connection_info
from bs4 import BeautifulSoup
from selenium.common import NoAlertPresentException
from datetime import datetime

class NaverKinBot(AsyncWorker):
    def __init__(self, bot_client_inbound) -> None:
        super().__init__(bot_client_inbound)
        self.account = {}
        self.user_session = {}
        self.configs = {}
        self.prev_account = ''
        self.running = False
        self.stop = False
        self.on_error = False
    
    async def execute_task(self, task: str):
        if task == "START":
            if not self.running:
                self.running = True
                asyncio.create_task(self.main())
        elif task == "STOP":
            self.stop = True
    
    async def init_driver(self):
        try:
            subprocess.call('taskkill /f /im chrome.exe /t')
        except:
            pass

        # options = uc.ChromeOptions()
        # options.add_argument('--disable-blink-features=AutomationControlled')
        # options.add_argument('--start-maximized')
        # options.add_argument('--disable-notifications')
        # options.add_argument("--disable-dev-shm-usage")
        # options.add_argument("--disable-popup-blocking")
        # await load_useragent(options=options, useragent=self.user_session['user_agent'])
        # prefs = {"credentials_enable_service": False,
        #         "profile.password_manager_enabled": False}
        # options.add_experimental_option("prefs", prefs)
        # while True:
        #     try:
        #         driver = uc.Chrome(options=options, use_subprocess=True, version_main=await get_chrome_browser_version())
        #         driver.maximize_window()
        #         pyautogui.press('esc')
        #         print("DRIVER INITIALIZED")
        #         break
        #     except Exception as e:
        #         print(e)
        #         continue
        driver = Driver(uc=True)
        return driver

    async def main(self):
        print("STARTED")

        # WAIT FOR SERVER TO SEND USERNAME/PASSWORD
        self.account = await self.data_queue.get()
        print(f"RECEIVED {self.account['username']} ACCOUNT")
        print(self.account)

        #WAIT FOR SERVER TO SEND USER SESSION
        self.user_session = await self.data_queue.get()
        print(self.user_session)

        #WAIT FOR SERVER TO SEND CONFIGS
        self.configs = await self.data_queue.get()
        print(self.configs)

        await update_state(state=2)

        self.driver = await self.init_driver()

        await short_sleep(5)
        await websocket_disconnect()
        await reconnect_modem(self.driver)
        await websocket_connect()

        await update_state(state=2)
        await get_connection_info()
        await short_sleep(30)

        await send_logging_data(level="info", log=f"{self.account['username']} HAS IP {await get_current_public_ip()}")
        print("SENT PUBLIC IP ADDRESS TO SERVER FOR LOGGING")
        await short_sleep(5)

        self.driver.uc_open_with_reconnect("https://kin.naver.com/", 10)
        await load_cookies(self.driver, self.user_session['cookies'])
        await short_sleep(5)
        self.driver.uc_open_with_reconnect("https://kin.naver.com/", 10)

        login_attempts = 0
        while login_attempts <= 2:
            if await logged_in(self.driver):
                break
            await self.login(self.driver)
            if login_attempts == 0:
                login_attempts += 1
                continue
            else:
                print("FAILED LOGIN ATTEMPT")
                await short_sleep(30)
                login_attempts += 1
            if login_attempts == 3:
                print(f"FAILED LOGGING IN WITH {self.account['username']}'s ACCOUNT! STOPPING PROGRAM")
                return False
            continue
        
        print(f"{self.account['username']} LOGGED IN")
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        await save_login(username=self.account['username'], ip_address=await get_current_public_ip(), login_timestamp=now)
        await short_sleep(5)
        await send_update_request(table="naver_accounts", data={"last_login": f"{await get_current_public_ip()} {now}"}, filters={"username": self.account["username"]})
        await short_sleep(5)
        await self.close_popups(self.driver)
        if not self.user_session["cookies"] or login_attempts != 0:
            await save_cookies(self.account["username"], self.driver)
        if not self.user_session["user_agent"] or login_attempts != 0:
            await save_user_agent(self.account["username"], self.driver)
        await self.get_account_url_and_level(driver=self.driver)
        return True
    
    async def login(self, driver: undetected.Chrome):
        await short_sleep(5)
        print("LOGGING IN")
        driver.uc_open_with_reconnect(r'https://nid.naver.com/nidlogin.login?url=https%3A%2F%2Fkin.naver.com%2F', 10)
        await bring_browser_to_front()
        pyautogui.press('esc')
        await self.authenticate(driver)
        await short_sleep(5)
    
    async def authenticate(self, driver: undetected.Chrome):
        await short_sleep(5)
        while True:
            try:
                driver.execute_script("document.getElementById('keep').click()")
                ip_security_label = driver.find_element('xpath', '//div[@class="ip_check"]//label[@for="switch"]//span[@class="blind"]').text
                if ip_security_label == "off":
                    print(f"IP SECURITY: {ip_security_label}")
                    break
                await short_sleep(1)
            except Exception as e:
                print(e)
                await short_sleep(1)
                continue
        await short_sleep(1)
        pyautogui.press('esc')
        pyperclip.copy(self.account['username'])
        await bring_browser_to_front()
        pyautogui.hotkey('ctrl', 'v')
        await short_sleep(5)
        await bring_browser_to_front()
        pyautogui.press('tab')
        await short_sleep(5)
        pyperclip.copy(self.account['password'])
        await bring_browser_to_front()
        pyautogui.hotkey('ctrl', 'v')
        await short_sleep(5)
        driver.uc_click("xpath", '//button[@id="log.login" and @type="submit"]')
    
    async def get_account_url_and_level(self, driver: undetected.Chrome):
        driver.uc_open_with_reconnect("https://kin.naver.com/myinfo/index.naver", 10)
        await short_sleep(1)
        account_url = driver.current_url
        self.account["account_url"] = account_url
        await self.close_popups(driver=driver)
        await short_sleep(1)

        level_gauge = driver.find_element("xpath", '//div[@id="level_guage"]/strong[@class="my_level"]').get_attribute("outerHTML")
        soup = BeautifulSoup(level_gauge, "lxml")
        [i.decompose() for i in soup.find_all('span', {'class' : 'level_number'})]
        [i.decompose() for i in soup.find_all('a', {'class' : 'guide'})]

        await send_update_request(table="naver_accounts", data={"level": soup.text, "account_url": account_url}, filters={"username": self.account["username"]})
    
    async def close_popups(self, driver: undetected.Chrome):
        await short_sleep(5)
        try:
            popups = driver.find_elements('xpath', '//div[contains(@class, "section_layer")]')
            for popup in popups:
                if popup.is_displayed():
                    popup_id = popup.get_attribute("id")
                    if "captcha" in popup_id:
                        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        print(f"CAPTCHA TRIGGERED {now} - {driver.current_url}")
                        self.stop = True
                        return False

                    a_close = popup.find_elements('xpath', './/a[@href="#" or contains(@class, "close") or .//span[contains(@class, "close")]]')
                    btn_close = popup.find_elements('xpath', './/button[@type="button" and contains(@class, "close")]')
                    if a_close:
                        driver.execute_script('arguments[0].click();', a_close[0])
                    elif btn_close:
                        driver.execute_script('arguments[0].click();', btn_close[0])
                    else:
                        print('Popup has no detected close button element')
                        return False
            return True
        except:
            print("No popup or popup can't be closed")
            return False
    
    async def handle_alerts(self, driver: undetected.Chrome):
        try:
            alert = driver.switch_to.alert
            if "등급에서 하루에 등록할 수 있는 답변 개수는" in alert.text:
                self.reached_id_limit = True
                alert.accept()
            else:
                alert.accept()
        except NoAlertPresentException as e:
            print("No alert box found")
        except Exception as e:
            print("HANDLE ALERT ERROR: " + e)