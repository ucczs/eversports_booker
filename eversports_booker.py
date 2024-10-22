#!/usr/bin/env python

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from pyvirtualdisplay import Display
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

import sys
import re
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# needs to be set by the user
from credentials import URL
from credentials import USERNAME
from credentials import PASSWORD

from config_reader import BookingConfig
import argparse
import os

import selenium_util
import time

import calendar
import datetime

from logger_format import get_logger

logger = get_logger(__name__)


def open_page_accept_cookies(driver, url):
    driver.get(url)
    driver.maximize_window()

    accept_cookies(driver)

def accept_cookies(driver) -> None:
    wait = WebDriverWait(driver, 10)

    x_path_preferences = '//*[@id="js_button-toggle-details"]'
    # x_path_preferences = '/html/body/div/div[1]/div[2]/div/div[3]/div/button'
    if not selenium_util.check_if_element_exists(driver, x_path_preferences):
        logger.error("Error: Cookies cannot be accepted, cookie preference field not found")
        sys.exit()

    selenium_util.pressButton(driver, x_path_preferences)

    xpath_accept = '//*[@id="confirmSelection"]'
    if not selenium_util.check_if_element_exists(driver, xpath_accept):
        logger.error("Error: Cookies cannot be accepted, cookie confirmation field not found")
        sys.exit()

    selenium_util.pressButton(driver, xpath_accept)


def login(driver):
    wait = WebDriverWait(driver, 10)
    time.sleep(1)

    x_path_login = '/html/body/div/header/div/div/div[2]/nav/ul/a[1]'
    selenium_util.pressButton(driver, x_path_login)


    x_path_username_field = '//*[@id=":R5tja:"]'
    x_path_password_field = '//*[@id=":R9tja:"]'

    wait.until(EC.presence_of_element_located((By.XPATH, x_path_username_field)))
    username_field = wait.until(EC.presence_of_element_located((By.XPATH, x_path_username_field)))
    password_field = wait.until(EC.presence_of_element_located((By.XPATH, x_path_password_field)))


    # Enter the credentials and submit the form
    username_field.send_keys(USERNAME)
    password_field.send_keys(PASSWORD)

    login_button_hover_xp = '/html/body/div/div/div/form/div/div/div/div[3]/button[1]'
    login_button_hover = driver.find_element(By.XPATH, login_button_hover_xp)

    actions = ActionChains(driver)
    actions.move_to_element(login_button_hover).perform()

    x_path_login_button = '/html/body/div/div/div/form/div/div/div/div[3]/button[1]'
    selenium_util.pressButton(driver, x_path_login_button)



def is_valid_url(url):
    pattern = re.compile(r'https?://www\.[\w.-]+\.[a-z]{2,}')
    match = pattern.match(url)

    return bool(match)


def next_week(driver):
    wait = WebDriverWait(driver, 10)
    xpath_next_week_button = "/html/body/div/main/div[3]/div/div/div[1]/div[1]/div/button[2]"
    if not selenium_util.check_if_element_exists(driver, xpath_next_week_button):
        logger.error("Error: Next week button not found")
        sys.exit()

    wait.until(EC.presence_of_element_located((By.XPATH, xpath_next_week_button)))
    next_week_button = driver.find_element(By.XPATH, xpath_next_week_button)
    next_week_button.click()
    time.sleep(1)
    wait.until(selenium_util.wait_for_page_to_load)


def bookSpot(driver, weekday, time_slot, workout_type):
    weekday_mapping = {day: idx for idx, day in enumerate(calendar.day_name, 1)}

    today = datetime.datetime.today()
    date_in_two_weeks = today + datetime.timedelta(weeks=2)

    logger.info(f"Attempt to book {workout_type} at {time_slot}, {weekday}, {date_in_two_weeks.strftime('%Y-%m-%d')}")

    wait = WebDriverWait(driver, 10)

    weekday_idx = weekday_mapping[weekday]
    xpath_date = f'/html/body/div/main/div[3]/div/div/div[2]/div/div[1]/div/div/div[1]/div/div[{weekday_idx}]/ul/div'
    wait.until(EC.presence_of_element_located((By.XPATH, xpath_date)))

    date_field = driver.find_element(By.XPATH, xpath_date)
    date_raw = date_field.text.strip()
    for day_time in range(1,4):
        for workout_counter in range(1, 10):
            xpath_time = f'/html/body/div/main/div[3]/div/div/div[2]/div/div[1]/div/div/div[{day_time}]/div/div[{weekday_idx}]/ul/li[{workout_counter}]/div/div[1]'
            xpath_type = f'/html/body/div/main/div[3]/div/div/div[2]/div/div[1]/div/div/div[{day_time}]/div/div[{weekday_idx}]/ul/li[{workout_counter}]/div/div[2]'

            if not selenium_util.check_if_element_exists(driver, xpath_time):
                logger.debug(f"weekday={date_raw}, day_time={day_time}, workout_counter={workout_counter}")
                logger.debug("Time field not found")
                continue

            if not selenium_util.check_if_element_exists(driver, xpath_type):
                logger.debug(f"weekday={date_raw}, day_time={day_time}, workout_counter={workout_counter}")
                logger.debug("Type field not found")
                continue

            time_field = driver.find_element(By.XPATH, xpath_time)
            type_field = driver.find_element(By.XPATH, xpath_type)

            if(time_slot in time_field.text.strip() and workout_type == type_field.text.strip()):
                logger.debug(time_field.text.strip())
                logger.debug(type_field.text.strip())

                selenium_util.pressButton(driver, xpath_type)

                xpath_book_now = '/html/body/div[1]/main/div[2]/div[2]/div[4]/a/button/p'
                wait.until(EC.presence_of_element_located((By.XPATH, xpath_book_now)))
                selenium_util.pressButton(driver, xpath_book_now)

                time.sleep(10)

                xpath_finalize_booking = '/html/body/div/div[2]/div[2]/aside/div/div/div/div[1]/div/div/div/button/p'
                wait.until(EC.presence_of_element_located((By.XPATH, xpath_finalize_booking)))
                selenium_util.pressButton(driver, xpath_finalize_booking)

                xpath_booking_successful = '/html/body/div[2]/div[3]/div/div/div/div[1]/img'
                wait.until(EC.presence_of_element_located((By.XPATH, xpath_booking_successful)))
                logger.info("Booking successful!")
                break


def booking_desired(current_weekday_name, config_file):
    config = BookingConfig(config_file)
    workoutSlot = config.get_booking_of_weekday(current_weekday_name)

    desiredTime = None
    desiredType = None

    if(workoutSlot is None):
        logger.info("No booking desired for current weekday")
    else:
        desiredTime = workoutSlot.hour
        desiredType = workoutSlot.type
        logger.info(f"{desiredTime=}\n{desiredType=}")

    return desiredTime, desiredType


def parse_arguments():
    parser = argparse.ArgumentParser(description='Eversport booker for automating your eversports bookings')
    parser.add_argument('-c', '--config', type=str, required=True, help='Path to YAML config file. The config file lists the days, hours and types of workouts you want to book.')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('-hl', '--headless', action='store_true', help='Enable headless mode')
    parser.add_argument('-rp', '--raspi-mode', action='store_true', help='Enable raspi mode')

    args = parser.parse_args()

    config_path = args.config
    debug_mode = args.debug
    headless_mode = args.headless
    raspi_mode = args.raspi_mode

    if not os.path.isfile(config_path):
        raise argparse.ArgumentTypeError(f'{config_path} does not exist or is not a file')
    
    return config_path, debug_mode, headless_mode, raspi_mode


def main():
    config_path, debug_mode, headless_mode, raspi_mode = parse_arguments()

    current_weekday_name = datetime.datetime.now().strftime("%A")
    desiredTime, desiredType = booking_desired(current_weekday_name, config_path)

    if desiredType is None or desiredTime is None:
        return 0

    global g_courses

    if headless_mode:
        if raspi_mode:
            service = Service(executable_path='/usr/lib/chromium-browser/chromedriver')
        else:
            service = Service(executable_path=ChromeDriverManager().install())

        logger.debug("Start in headless mode")
        display = Display(visible=0, size=(1280, 720))
        display.start()
        options = Options()
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(service=service, options=options)
    else:
        logger.debug("Start in browser mode")
        # service = Service(executable_path=ChromeDriverManager().install())
        service = Service(executable_path='/home/fibonacci/.wdm/drivers/chromedriver/linux64/130.0.6723.58/chromedriver-linux64/chromedriver')

        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(service=service, options=options)

    if(is_valid_url(URL)):
        logger.debug("URL is valid!")
        open_page_accept_cookies(driver, URL)
        login(driver)
        time.sleep(2)
        next_week(driver)
        next_week(driver)

        bookSpot(driver, current_weekday_name, desiredTime, desiredType)
        time.sleep(5)
    else:
        logger.error("Provided URL has the wrong format!")
        sys.exit(1)

    driver.quit()

    if headless_mode:
        display.stop()

    return 0


if __name__ == "__main__":
    sys.exit(main())
