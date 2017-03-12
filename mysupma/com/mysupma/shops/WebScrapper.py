from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary


class WebScrapper:
    def __init__(self, url):
        binary = FirefoxBinary('/usr/bin/firefox')
        self.driver = webdriver.Firefox(firefox_binary=binary)

