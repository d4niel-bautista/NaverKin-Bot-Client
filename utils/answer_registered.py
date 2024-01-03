import asyncio

async def check_answer_registered(driver, question_link: str, account_url: str, handle_alerts):
    try:
        if not account_url:
            return False
        driver.default_get(question_link)
        await handle_alerts(driver)
        await asyncio.sleep(5)
        while True:
            next_page_btn = driver.find_elements('xpath', '//a[@id="nextPageButton"]')
            if next_page_btn:
                if next_page_btn[0].is_displayed():
                    next_page_btn[0].uc_click()
                    await asyncio.sleep(5)
                    continue
            await asyncio.sleep(5)
            break
        answer_list = driver.find_element('xpath', '//div[@class="answer-content__list _answerList"]')
        answer = answer_list.find_element('xpath', f'.//a[contains(@href, "{account_url}")]')
        if answer:
            return True
    except Exception as e:
        print("error on check answer registered")
        print(e)
        return False