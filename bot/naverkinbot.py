from .async_worker import AsyncWorker
import asyncio
import subprocess
import undetected_chromedriver as uc
from utils import get_chrome_browser_version, reconnect_modem, bring_browser_to_front, short_sleep
from .session_manager import load_useragent, load_cookies, logged_in
import pyautogui
import pyperclip

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

        options = uc.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-notifications')
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-popup-blocking")
        await load_useragent(options=options, useragent=self.user_session['user_agent'])
        prefs = {"credentials_enable_service": False,
                "profile.password_manager_enabled": False}
        options.add_experimental_option("prefs", prefs)
        while True:
            try:
                driver = uc.Chrome(options=options, use_subprocess=True, version_main=await get_chrome_browser_version())
                driver.maximize_window()
                print("DRIVER INITIALIZED")
                break
            except Exception as e:
                print(e)
                continue
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

        self.driver = await self.init_driver()
        await reconnect_modem(self.driver)
        await short_sleep(5)
        self.driver.get("https://kin.naver.com/")
        await load_cookies(self.driver, self.user_session['cookies'])
        await short_sleep(5)
        self.driver.get("https://kin.naver.com/")
        if not await logged_in(self.driver):
            await self.login(self.driver)
        print(f"{self.account['username']} LOGGED IN")
        await short_sleep(5)
        await self.close_popups(self.driver)
    
    async def login(self, driver: uc.Chrome):
        await short_sleep(5)
        print("LOGGING IN")
        driver.get(r'https://nid.naver.com/nidlogin.login?url=https%3A%2F%2Fkin.naver.com%2F')
        await bring_browser_to_front()
        pyautogui.press('esc')
        await self.authenticate(driver)
        await short_sleep(5)
    
    async def authenticate(self, driver: uc.Chrome):
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
        login_btn = driver.find_element('xpath', '//*[@id="log.login"]')
        login_btn.click()
    
    async def close_popups(self, driver: uc.Chrome):
        await short_sleep(5)
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
    