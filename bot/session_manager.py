import asyncio
import json

async def load_cookies(driver, cookies):
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

async def save_cookies(username, service, driver):
    service.save_cookies(username, json.dumps(driver.get_cookies()))
    await asyncio.sleep(5)

async def save_useragent(username, service, driver):
    useragent = driver.execute_script("return navigator.userAgent;")
    service.save_useragent(username, useragent)
    await asyncio.sleep(5)

async def logged_in(driver):
    await asyncio.sleep(5)
    login_btn = driver.find_elements('xpath', '//div[@class="header_gnb__cell"]//a[@id="gnb_login_button"]')
    if login_btn:
        if login_btn[0].is_displayed():
            return False
    return True