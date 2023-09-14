from undetected_chromedriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time, os
from dotenv import load_dotenv
load_dotenv()
from utils import get_chrome_browser_version

USER = os.getenv('MODEM_USERNAME')
PASS = os.getenv('MODEM_PASSWORD')
def login (driver):
    driver.get('http://192.168.100.1/')

    print('Login To Modem')
    time.sleep(1.8)

    try:
        # Username Field
        time.sleep(3.3)
        username_element = driver.find_element(By.ID, 'username')
        username_element.send_keys(USER)

        # Password Field
        time.sleep(3.3)
        password_element = driver.find_element(By.ID, 'password')
        password_element.send_keys(PASS)

        # Login Button
        time.sleep(3.3)
        wait = WebDriverWait(driver, 10)
        login_confirmation_element = wait.until(EC.element_to_be_clickable((By.ID, 'login')))
        login_confirmation_element.click()

        # Check if login is success find this element
        time.sleep(10)
        driver.find_element(By.ID, 'menu')
    except Exception as e:
        print('Login Failed')
        print('Login Exception', e)
        return False
    else:
        print('Login Success')

    return True

def start(driver):
    if login(driver):
        try:
            print('Program will start re-connecting modem...')
            time.sleep(10)
            driver.switch_to.frame(driver.find_element(By.ID, 'mainifr'))

            wait = WebDriverWait(driver, 10)
            apply_element = wait.until(EC.element_to_be_clickable((By.ID, 'apply')))

            select_element= Select(driver.find_element(By.ID, 'connect'))
            time.sleep(30)

            print('Disconnecting the modem...')
            select_element.select_by_value('1')
            apply_element.click()
            time.sleep(60)

            confirms = driver.find_elements(By.CSS_SELECTOR, '.xubox_layer div.xubox_main .xubox_botton a.xubox_yes')

            for confirm in confirms:
                if confirm.is_displayed():
                    confirm.click()

            time.sleep(30)

            print('Re-connecting the modem...')
            select_element.select_by_value('0')
            apply_element.click()
            time.sleep(60)

            confirms = driver.find_elements(By.CSS_SELECTOR, '.xubox_layer div.xubox_main .xubox_botton a.xubox_yes')

            for confirm in confirms:
                if confirm.is_displayed():
                    confirm.click()

            time.sleep(30)

            print('Modem is now connected...')
            time.sleep(30)
        except Exception as e:
            print('Program Error: ', e)

""" START PROGRAM """
def reconnect_modem(driver):
    try:
        # Get the screen size
        screen_width = driver.execute_script('return window.screen.availWidth')
        screen_height = driver.execute_script('return window.screen.availHeight')
        # Set the window size to half of the screen width and full screen height
        driver.set_window_size(screen_width // 1.5, screen_height)
        # Set the window position to the left half of the screen
        driver.set_window_position(0, 0)

        # Starting the program for the first time
        start(driver)
        print('Program Closing in 20 seconds...')
        time.sleep(20)
    except Exception as e:
        print('Program Error: ', e)