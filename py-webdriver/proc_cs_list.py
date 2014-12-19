import os
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import json
from selenium.webdriver.remote.webelement import WebElement
import time
from selenium.webdriver.common.action_chains import ActionChains
import hashlib
from py_sel import PySel
from hash_cache import HashFileCache
import datetime

LOOP_MAX = 300

RETRY_MAX = 5
DIR_OUT = "out-cs"
BOX_COUNT = 24

class ProcCsList(PySel):

#     def _loadUrl(self, url):
#         if os.path.exists(self.digfp):
#             lastUrl = self.readf(self.digfp)
#             if lastUrl is not None:
#                 self.driver.get(lastUrl)
#                 return
#         self.driver.get(url)

    def __init__(self):
        self.driver = self.buildDriver()

        self.cache = HashFileCache(DIR_OUT)

        # dig = self._calcDig(url)
        # self.digfp = os.path.join(DIR_OUT, dig)

        if not os.path.exists(DIR_OUT):
            os.mkdir(DIR_OUT)

        self.__default = dict()

    def setEntry(self, url):
        self.entryUrl = url

#         xp24 = ".//div[@class='result-count-switch']//ul/li/a[@class != 'current' and contains(text(), '24')]"
#         page24 = self._firstNode(self.driver, xp24)
#         if page24 is None:
#             print("no found page24")
#         else:
#             page24.click()

    def procBox(self, box):
        boundle = dict()

        for k in self.__default:
            boundle[k] = self.__default[k]

        title = self._firstText(box, "./h2/a[@href and @recordid]")
        if title is None:
            return
        boundle["title"] = title

        price = self._firstAttr(box, ".//div[@class='primary-price ']/p/a[@href] | .//div[@class='primary-price special-offer-price']/p/a[@href]", "data-price")
        boundle["price"] = price

        boundle["engine"] = self._firstText(box, ".//li[@class='item-engine']")
        boundle["trans"] = self._firstText(box, ".//li[@class='item-transmission']")
        boundle["body"] = self._firstText(box, ".//li[@class='item-body']")
        boundle["odometer"] = self._firstText(box, ".//li[@class='item-odometer']")
        boundle["state"] = self._firstText(box, ".//div[@class='call-to-action']/p")
        boundle["op_time"] = str(datetime.datetime.now())

        anchor = self._firstNode(box, ".//div[@class='call-to-action']/a[@href and text() = 'View']")

        priImg = self._firstNode(box, ".//div/ul[@class='image-thumbs']/li[@class='primary']/a[@href]/img[@src]")
        if priImg is None:
            boundle["pri-img"] = "na"
        else:
            boundle["pri-img"] = priImg.get_attribute("src")
        secImages = box.find_elements_by_xpath(".//div/ul[@class='image-thumbs']/li[@class='secondary']/a[@href]/img[@src]")
        pending = []
        for img in secImages:
            pending.append(img.get_attribute("src"))
        boundle["sec-img"] = pending

        if anchor is not None:
            boundle["recordid"] = anchor.get_attribute("recordid")
            boundle["href"] = anchor.get_attribute("href")
            fp = self._buildFp(DIR_OUT, boundle["recordid"])
            self.writef(fp, json.dumps(boundle, indent=0, sort_keys=True))


    def __loadFirstPage(self):

        # load entry url
        self.driver.get(self.entryUrl)
        # switch to 24 items per page
        c24xp = ".//div[@class='result-count-switch']/ul/li/a[contains(text(), '24')]"

        btn24 = self._firstNode(self.driver, c24xp)
        if btn24 is None:
            self.info("no found btn-24")
        else:
            self._clickToNextPage(self.driver, c24xp)
            # btn24.click()
            time.sleep(3)
            # self.info("do nothing")

        self.entryDig = self._calcDig(self.entryUrl)
        if self.cache.exists(self.entryUrl):
            newUrl = self.cache.fetch(self.entryUrl)
            self.driver.get(newUrl)

    def execute(self):

        self.__loadFirstPage()

        xpNext = ".//ul/li[@class='next']/a[@id and text() = 'Next ']"
        xpBox = ".//div[contains(@class, 'result-set-container')]/div[contains(@class, 'result-item')]"

        for i in range(LOOP_MAX):
            needBreak = False

            for j in range(RETRY_MAX):
                boxes = self.driver.find_elements_by_xpath(xpBox)
                # nexts = self.driver.find_elements_by_xpath(xpNext)
                if len(boxes) >= BOX_COUNT:
                    break
                time.sleep(1)
            else:
                self.info("NO found enough box to continue: %d" % (len(boxes)))
                needBreak = True

            self.info("found %d box/s of page %d" % (len(boxes), i))

            for box in boxes:
                self.procBox(box)

            if needBreak:
                break

            if self._clickToNextPage(self.driver, xpNext):
                url = self.driver.current_url
                # self.writef(self.digfp, url)
                self.cache.store(self.entryUrl, url)
                continue

            self.info("NO found next to continue")
            break

    def destroy(self):
        if self.driver is not None:
            self.driver.close()
            self.driver.quit()
            self.driver = None


    def setKv(self, k, v):
        print("setkv::%s=%s" % (k, v))
        self.__default[k] = v



def splitKv(raw):
    subs = raw.split('=', 1)
    if 2 == len(subs):
        return subs[0], subs[1]
    return None, None


def main():
    pl = ProcCsList()
    for url in sys.argv[1:]:
        if url.startswith('@'):
            fp = url[1:]
            lines = []
            with open(fp, "r") as f:
                lines = f.readlines()
            if len(lines) > 0:
                for line in lines:
                    ln = line.strip()
                    if ln.startswith('#'):
                        continue
                    if len(ln) < 1:
                        continue
                    pl.setEntry(ln)
                    pl.execute()
        else:
            # pl.setEntry(url)
            # pl.execute()
            k, v = splitKv(url)
            if k is not None:
                pl.setKv(k, v)

    pl.destroy()

if __name__ == '__main__':
    exit(main())
