import time

def load_cookies(driver, cookies):
    for cookie in cookies:
        for key, val in cookie.items():
            if key == 'domain':
                print(val)
                driver.get(val)
                time.sleep(5)
                driver.add_cookie(cookie)
                break

def load_useragent(options, useragent):
    if useragent:
        options.add_argument(f'--user-agent={useragent}')

def save_cookies(username, service, driver):
    service.save_cookies(username, driver.get_cookies())
    time.sleep(5)