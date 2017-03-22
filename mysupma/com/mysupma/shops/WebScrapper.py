import os

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

import sqlite3

class WebScrapper:

    def __init__(self, url):
        profileDir = os.path.expanduser("~/workspace/firefoxprofile/")
        profile = webdriver.FirefoxProfile(profileDir)
        binary = FirefoxBinary('/usr/bin/firefox')
        # profile = webdriver.FirefoxProfile()
        # profile.set_preference('browser.download.folderList', 2)
        # profile.set_preference('browser.download.manager.showWhenStarting', False)
        # profile.set_preference('browser.download.dir', os.getcwd())
        # profile.set_preference('browser.helperApps.neverAsk.saveToDisk',
        #                        ('application/vnd.ms-excel'))
        self.driver = webdriver.Firefox(firefox_binary=binary, firefox_profile=profile)
        self.conn = None
        # dbFp = "mysupma1.db"
        # if os.path.exists(dbFp):
        #     self.conn = sqlite3.connect(dbFp)
