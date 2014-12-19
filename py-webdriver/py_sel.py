import hashlib
import json
import os
import time

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.remote.webelement import WebElement
import sys

RETRY_MAX = 9

class PySel:

    @staticmethod
    def _buildFp(baseDir, recordId):
        ch2 = recordId[-2:]
        dir2 = os.path.join(baseDir, ch2)
        if not os.path.exists(dir2):
            os.mkdir(dir2)
        return os.path.join(dir2, "%s.json" % (recordId))

    @staticmethod
    def writef(fp, body):
        with open(fp, "w") as f:
            f.write(body)

    @staticmethod
    def _calcDig(raw):
        m = hashlib.sha1()
        m.update(raw)
        return m.hexdigest()

    @staticmethod
    def readf(fp):
        ctx = None
        with open(fp, "r") as f:
            ctx = f.read()
        return ctx

    @staticmethod
    def buildDriver():
        fp = webdriver.FirefoxProfile("D:/apps/fireprofile")
        # fp = webdriver.FirefoxProfile("C:/Temp/workspace/_fireprofile/_sel+abp")
        # fp = webdriver.FirefoxProfile()
        # fp.set_preference('permissions.default.stylesheet', 2)
        fp.set_preference('permissions.default.image', 2)
        fp.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
        # fp.set_preference("browser.link.open_newwindow", 2)
        drv = webdriver.Firefox(firefox_profile=fp)
        drv.set_page_load_timeout(30)
        return drv

    def _firstText(self, node, xp):
        els = node.find_elements_by_xpath(xp)
        if els is None:
            return None
        for el in els:
            return el.text.strip()
        return None

    def _firstAttr(self, node, xp, attrName):
        els = node.find_elements_by_xpath(xp)
        if els is None:
            return None
        for el in els:
            return el.get_attribute(attrName)
        return None

    def _firstNode(self, node, xp):
        els = node.find_elements_by_xpath(xp)
        if els is None:
            return None
        for el in els:
            return el
        return None

    @staticmethod
    def _clickTillUrlChange(driver, el):
        currUrl = driver.current_url
        for j in range(RETRY_MAX):
            sys.stdout.write('.')
            el.click()
            time.sleep(1)
            if driver.current_url != currUrl:
                return True

        print("url NO change")
        return False

    @staticmethod
    def _clickToNextPage(driver, xp):
        els = None
        for j in range(RETRY_MAX):
            els = driver.find_elements_by_xpath(xp)
            if els is not None and len(els) > 0:
                break
            time.sleep(1)
            sys.stdout.write(':')
        else:
            return False

        el = els[0]

        currUrl = driver.current_url
        for j in range(RETRY_MAX):
            sys.stdout.write('.')
            el.click()
            time.sleep(2)
            if driver.current_url != currUrl:
                return True

        print("url is NOT changed")
        return False

    @staticmethod
    def _keyAndClick(driver, key, el):
        clicker = ActionChains(driver)
        clicker.key_down(key).click(el).key_up(key).perform()
        time.sleep(2)

    @staticmethod
    def _shiftClick(driver, el):
        origHandles = driver.window_handles
        PySel._keyAndClick(driver, Keys.SHIFT, el)
        for handle in driver.window_handles:
            if handle not in origHandles:
                return handle

        PySel.info("none new handle")
        return None

    @staticmethod
    def info(s): print(s)
