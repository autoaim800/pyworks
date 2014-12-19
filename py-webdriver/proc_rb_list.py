import os
import sys
from selenium import webdriver
from proc_cs_list import ProcList
from urlparse import urlparse
import selenium
import time
import json

DIR_OUT = "output-rb"
LOOP_MAX = 1000
RETRY_MAX = 6

class ProcRbList(ProcList):

    def procBack(self):
        url1 = self.driver.current_url
        for i in range(RETRY_MAX):
            self.driver.back()
            time.sleep(1)
            if self.driver.current_url != url1:
                break
            time.sleep(1)

    def _loadUrl(self, url):
        if os.path.exists(self.digfp):
            lastUrl = self.readf(self.digfp)
            if lastUrl is not None:
                self.driver.get(lastUrl)
                return
        self.driver.get(url)

    def __init__(self, url):
        self.driver = self.buildDriver()

        dig = self._calcDig(url)
        self.digfp = os.path.join(DIR_OUT, dig)

        if not os.path.exists(DIR_OUT):
            os.mkdir(DIR_OUT)

        self._loadUrl(url)

    def destroy(self):
        if self.driver is not None:
            self.driver.close()
            self.driver.quit()
            self.driver = None


    def __extractModel(self, raw):
        if raw is None:
            return None

        subs = raw.split(';')
        for sub in subs:
            if sub.count("|") < 1:
                return sub
        return None


    def __buildKvm(self, raw):
        pending = dict()
        subs = raw.split("&")
        for sub in subs:
            items = sub.split('=', 1)
            pending[items[0]] = items[1]
        return pending


    def proc1View(self):
        spans = self.driver.find_elements_by_xpath(".//div/span[@class='content']")
        for span in spans:
            for j in range(RETRY_MAX):
                try:
                    span.click()
                    break
                except selenium.common.exceptions.ElementNotVisibleException:
                    time.sleep(1)
            time.sleep(0.2)

        # time.sleep(1)

        url = self.driver.current_url
        up = urlparse(url)
        kvm = self.__buildKvm(up.query)
        rbId = None
        if "R" in kvm:
            rbId = kvm["R"]

        if rbId is None:
            self.info("no found rb-id")
            return

        boundle = dict()
        boundle["url"] = url
        boundle["redid"] = rbId
        boundle["title"] = self._firstText(self.driver, ".//div[@class='title-panel']/h1[@class='details-title']")
        boundle["z_make"] = self._firstAttr(self.driver, ".//meta[@name='WT.z_make']", "content")
        boundle["z_price"] = self._firstAttr(self.driver, ".//meta[@name='WT.z_price']", "content")
        boundle["z_year"] = self._firstAttr(self.driver, ".//meta[@name='WT.z_year']", "content")
        rawModel = self._firstAttr(self.driver, ".//meta[@name='WT.z_model']", "content")
        boundle["z_model"] = self.__extractModel(rawModel)

        xpLabel = ".//tr/td[@class='item']//tr/td[position() = 1 and @class='label']"
        els = self.driver.find_elements_by_xpath(xpLabel)
        for td1 in els:
            td2 = self._firstNode(td1, "../td[@class='value']")
            val = td2.text.strip()
            key = td1.text.strip()
            boundle[key] = val

            fp = self._buildFp(DIR_OUT, boundle["redid"])
            self.writef(fp, json.dumps(boundle))

    def proc1More(self):
        xpNext = ".//ul[@class='pagination']/li[@class='next']/a[@href and text() = 'Next']"
        xpDetail = ".//div/span[@class='view-more' and text() = 'more details']"
        nextc = 0
        for i in range(LOOP_MAX):
            details = self.driver.find_elements_by_xpath(xpDetail)
            detailc = len(details)
            self.info("found %d at L2" % (detailc))
            for i in range(detailc):
                for j in range(RETRY_MAX):
                    details = self.driver.find_elements_by_xpath(xpDetail)
                    if details is not None and len(details) == detailc:
                        break
                    time.sleep(1)
                else:
                    self.info("trick length mismatch at L2")
                    break
                self._clickTillUrlChange(self.driver, details[i])
                self.proc1View()
                self.procBack()

            if self._clickToNextPage(self.driver, xpNext):
                nextc += 1
            else:
                self.info("failed clicking next at L2")
                break

        for i in range (nextc):
            self.procBack()

    def execute(self):
        xpNext = ".//ul[@class='pagination']/li[@class='next']/a[@href and text() = 'Next']"
        xpMore = ".//div[@class='right']/span[@class='view-more' and text() = 'view more']"
        for i in range(LOOP_MAX):
            mores = self.driver.find_elements_by_xpath(xpMore)
            morec = len(mores)
            self.info("found %d at L1" % (morec))

            for i in range(morec):
                self.info("#%d/%d at L1" % (i, morec))
                for j in range(RETRY_MAX):
                    mores = self.driver.find_elements_by_xpath(xpMore)
                    if len(mores) == morec:
                        break
                    time.sleep(2)
                else:
                    self.info("trick length mismatch at L1")
                    break
                self._clickTillUrlChange(self.driver, mores[i])

                self.proc1More()

                self.procBack()

            if self._clickToNextPage(self.driver, xpNext):
                self.writef(self.digfp, self.driver.current_url)
            else:
                self.info("failed clicking next at L1")
                break


def main():
    pl = ProcRbList(sys.argv[1])
    pl.execute()
    pl.destroy()
if __name__ == '__main__':
    exit(main())
