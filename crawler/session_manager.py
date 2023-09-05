import time

def load_cookies(driver, cookies):
    grouped_cookies = {}
    for cookie in cookies:
        if cookie['domain'][0] == '.':
            domain = cookie['domain'][1:]
        else:
            domain = cookie['domain']
        if not domain in grouped_cookies.keys():
            grouped_cookies[domain] = []
        grouped_cookies[domain].append(cookie)
    for i in grouped_cookies:
        driver.get('https://' + i)
        time.sleep(2)
        for j in grouped_cookies[i]:
            driver.add_cookie(j)
        time.sleep(5)

def load_useragent(options, useragent):
    if useragent:
        options.add_argument(f'--user-agent={useragent}')

def save_cookies(username, service, driver):
    service.save_cookies(username, driver.get_cookies())
    time.sleep(5)