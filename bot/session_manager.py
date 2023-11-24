import asyncio
from networking.service import send_update_request
import json

async def load_cookies(driver, cookies):
    try:
        cookies = json.loads(cookies)
    except:
        print(f"INVALID COOKIES {cookies}")
        return
    if cookies:
        for cookie in cookies:
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                print(e)
                continue

async def load_useragent(options, useragent):
    if useragent:
        options.add_argument(f'--user-agent={useragent}')

async def save_cookies(username, driver):
    await asyncio.sleep(5)
    cookies = json.dumps(driver.get_cookies())
    await send_update_request('user_sessions', data={"cookies": cookies}, filters={"username": username})

async def save_user_agent(username, driver):
    await asyncio.sleep(5)
    user_agent = driver.execute_script("return navigator.userAgent;")
    await send_update_request('user_sessions', data={"user_agent": user_agent}, filters={"username": username})
    
async def logged_in(driver):
    await asyncio.sleep(5)
    captcha_widget = [i for i in driver.find_elements('xpath', '//div[@class="captcha_wrap"]') if i.is_displayed()]
    if captcha_widget:
        return False
    invalid_login = [i for i in driver.find_elements('xpath', '//div[@class="login_error_wrap"]') if i.is_displayed()]
    if invalid_login:
        return False
    login_btn = [i for i in driver.find_elements('xpath', '//div[@class="header_gnb__cell"]//a[@id="gnb_login_button"]') if i.is_displayed()]
    if login_btn:
        return False
    return True