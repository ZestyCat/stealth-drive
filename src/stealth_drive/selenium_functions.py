from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def fill_form(driver, text, element, by = By.ID, timeout=10):
    input = WebDriverWait(driver, timeout).until( \
        EC.presence_of_element_located((by, element)))
    input.clear()
    input.send_keys(text)
   
def click_item(driver, element, by = By.ID, timeout=10, js_click=True):
    WebDriverWait(driver, timeout).until( \
        EC.element_to_be_clickable((by, element)))
    btn = driver.find_element(by, element)
    if js_click:
        driver.execute_script("arguments[0].click();", btn)
    else:
        btn.click()
    
def get_element_text(driver, element, by = By.ID, timeout=10):
    WebDriverWait(driver, timeout).until( \
        EC.presence_of_element_located((by, element)))
    ele = driver.find_element(by, element)
    return ele.text

def check_loaded(driver, element, by=By.ID, timeout=10):
    WebDriverWait(driver, timeout).until( \
            EC.presence_of_element_located((by, element)))

def get_element(driver, element, by = By.ID, timeout=10):
    WebDriverWait(driver, timeout).until( \
        EC.presence_of_element_located((by, element)))
    ele = driver.find_element(by, element)
    return ele

def get_elements(driver, element, by = By.ID, timeout=10):
    WebDriverWait(driver, timeout).until( \
        EC.presence_of_element_located((by, element)))
    ele = driver.find_elements(by, element)
    return ele
