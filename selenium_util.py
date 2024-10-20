
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def check_if_element_exists(driver, xpath):
    try:
        _ = driver.find_element(By.XPATH, xpath)
        return True
    except:
        return False

def pressButton(driver, xpath):
    wait = WebDriverWait(driver, 10)

    wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    login_button = driver.find_element(By.XPATH, xpath)
    login_button.click()

def wait_for_page_to_load(driver):
    return driver.execute_script("return document.readyState") == "complete"
