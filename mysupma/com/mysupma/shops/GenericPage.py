from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


TIMEOUT = 20


def waitforXpath(driver, xpath):
    cond = EC.presence_of_element_located((By.XPATH, xpath))
    el = WebDriverWait(driver, TIMEOUT).until(cond)
    return el


class GenericPage:
    def __init__(self, webdriver):
        self.driver = webdriver

    def findElements(self, xpath):
        return self.driver.find_elements_by_xpath(xpath)

