import os
import sys
from py_sel import PySel
from hash_cache import HashFileCache
from selenium.common.exceptions import NoSuchElementException
import time
import sqlite3
import hashlib

DIR_CACHE = "rb-cache"
DB_NAME = "rb2.db"

PAGE_MAX = 1000
LOOP_MAX = 200

XP_T1_ANCHOR = ".//div[@class='csn-results']/div[@class='content']/a[@href and @id]"
XP_T1_NEXT = ".//div[@class='r-module footer-paging']//ul[@class='pagination']/li[@class='next']/a[@href and text() = 'Next']"

DDL = """
create table t_links(
    url_hash varchar(40),
    url_text text,
    primary key(url_hash)
);

create table t_entry(
    entry_hash varchar(40),
    entry_sta varchar(10),
    point_hash varchar(40),
    op_time datetime,
    primary key(entry_hash)
);

create table t_paging(
    entry_hash varchar(40),
    paging_hash varchar(40),
    op_time datetime,
    primary key (entry_hash, paging_hash)
);

create table t_tier1(
    entry_hash varchar(40),
    tier1_hash varchar(40),
    op_time datetime,
    primary key(entry_hash, tier1_hash)
);

create table t_tier2(
    entry_hash varchar(40),
    tier2_hash varchar(40),
    op_time datetime,
    primary key(entry_hash, tier2_hash)
);

create table t_item(
    entry_hash varchar(40),
    item_hash varchar(40),
    op_time datetime,
    primary key (entry_hash, item_hash)
);

"""


class PagingLister(object):

    def __init__(self, driver):
        self.driver = driver

    def loadUrl(self, url):
        self.url = url
        self.driver.get(url)

    def extractUrlList(self):
        pending = []
        anchorList = self.driver.find_elements_by_xpath(XP_T1_ANCHOR)
        for anchor in anchorList:
            url = anchor.get_attribute("href")
            pending.append(url)
        return pending

    def obtainNextAnchor(self):
        try:
            return self.driver.find_element_by_xpath(XP_T1_NEXT)
        except NoSuchElementException:
            pass
        return None


class Tier1Lister(object):

    def __init__(self, driver):
        self.driver = driver


    def loadUrl(self, dig, url):
        self.url = url
        self.dig = dig
        self.driver.get(url)

    def extractUrlList(self):
        pending = []
        anchorList = self.driver.find_elements_by_xpath(XP_T1_ANCHOR)
        for anchor in anchorList:
            url = anchor.get_attribute("href")
            pending.append(url)
        return pending

    def obtainNextAnchor(self):
        try:
            return self.driver.find_element_by_xpath(XP_T1_NEXT)
        except NoSuchElementException:
            pass
        return None

class TouchRedbook(PySel):

    def __init__(self, entryUrl):
        self.entryUrl = entryUrl
        self.entryDig = self.__calcDig(entryUrl)

        self.driver = self.buildDriver()

        self.cache = HashFileCache(DIR_CACHE)

        if os.path.exists(DB_NAME):
            self.db = sqlite3.connect(DB_NAME)
        else:
            self.db = sqlite3.connect(DB_NAME)
            self.db.executescript(DDL)

        self.__registerEntry(self.entryUrl, self.entryDig)

    def __registerEntry(self, entryUrl, entryDig):
        c = self.db.cursor()
        try:
            cmd = " insert into t_links (url_hash, url_text) values (?, ?) "
            c.execute(cmd, (entryDig, entryUrl))
        except sqlite3.IntegrityError:
            pass

        cmd = """ insert into t_entry (entry_hash, entry_sta, op_time) 
            values ("%s", "na", datetime('now') ) """ % (self.entryDig)
        try:
            self.db.execute(cmd)
        except sqlite3.IntegrityError:
            pass

    def __updateEntry(self, sta, dig):
        cmd = """ update t_entry 
            set entry_sta = "%s", point_hash = "%s"
            where entry_hash = "%s"
        """ % (sta, dig, self.entryDig)

        self.db.execute(cmd)

    def __calcDig(self, raw):
        return hashlib.sha1(raw).hexdigest()

    def __queryResumePoint(self):
        """query last t1-url from dB"""

        cmd = """select a.entry_sta, a.point_hash, c.url_text
        from t_entry a        
        left join t_links c on a.point_hash = c.url_hash
        """

        for row in self.db.execute(cmd):
            sta = row[0]
            dig = row[1]
            url = row[2]
            return sta, dig, url
        return None, None


    def __insertTwoUrl(self, url, tblName):

        cmd1 = """ insert into t_%s(entry_hash, %s_hash, op_time) 
                values ("%%s", "%%s", datetime('now')) """ \
                % (tblName, tblName)

        cmd2 = """ update t_%s set op_time = datetime('now') 
                where entry_hash = "%%s" and %s_hash = "%%s" """ \
                % (tblName, tblName)

        dig = self.__calcDig(url)
        c = self.db.cursor()
        try:
            cmd = " insert into t_links (url_hash, url_text) values (?, ?) "
            c.execute(cmd, (dig, url))
        except sqlite3.IntegrityError:
            pass

        try:
            cmd = cmd1 % (self.entryDig, dig)
            c.execute(cmd)
        except sqlite3.IntegrityError:
            cmd = cmd2 % (self.entryDig, dig)
            c.execute(cmd)

    def __registerT1(self, urls):
        for url in urls:
            self.__insertTwoUrl(url, "tier1")

    def __registerItem(self, urlList):
        for url in urlList:
            self.__insertTwoUrl(url, "item")

    def __registerPaging(self, pagingUrl):
        self.__insertTwoUrl(pagingUrl, "paging")

    def procPaging(self, url):

        pl = PagingLister(self.driver)
        pl.loadUrl(url)

        for i in range(PAGE_MAX):
            currUrl = self.driver.current_url

            noMore = False

            urlList = pl.extractUrlList()
            nextAnchor = pl.obtainNextAnchor()
            if nextAnchor is None:
                noMore = True
            else:
                nextAnchor.click()
                time.sleep(1)

            self.__registerPaging(currUrl)
            self.__registerT1(urlList)
            self.__updateEntry("paging", self.__calcDig(currUrl))

            self.db.commit()

            # progress bar
            sys.stderr.write('.')

            if noMore: break

    def __procTier1Page1(self, dig, url):

        self.__updateEntry("tier1", dig)

        tl = Tier1Lister(self.driver)
        tl.loadUrl(dig, url)

        for i in range(PAGE_MAX):
            self.__registerItem(tl.extractUrlList())
            nextAnchor = tl.obtainNextAnchor()
            if nextAnchor is None:
                break
            nextAnchor.click()

        self.db.commit()

    def __procItemPage1(self, dig, url):

        self.__updateEntry("item", dig)

        if not self.cache.exists(url):
            self.driver.get(url)
            ctx = self.driver.page_source
            self.cache.store(url, ctx.encode("ascii", "ignore"))

        self.db.commit()

    def procItem(self, resumeDig):
        cmd = """select a.item_hash, b.url_text
        from t_item a
        left join t_links b on a.item_hash = b.url_hash
        order by a.op_time asc
        """
        if resumeDig is None:
            self.info("begin for item")
            for row in self.db.execute(cmd):
                dig = row[0]
                url = row[1]
                self.__procItemPage1(dig, url)
        else:
            skipC = 0
            self.info("resume for item")
            found = False
            for row in self.db.execute(cmd):
                dig = row[0]
                url = row[1]
                if found:
                    self.__procItemPage1(dig, url)
                else:
                    if dig == resumeDig:
                        found = True
                        self.info("skipped %d" % (skipC))
                        self.__procItemPage1(dig, url)
                    else:
                        skipC += 1

    def procTier1(self, resumeDig):
        cmd = """ select a.tier1_hash, b.url_text
            from t_tier1 a
            left join t_links b on a.tier1_hash = b.url_hash 
            order by a.op_time asc """

        if resumeDig is None:
            self.info("begin for tier1")
            for row in self.db.execute(cmd):
                dig = row[0]
                url = row[1]
                self.__procTier1Page1(dig, url)
        else:
            self.info("resume for tier1")
            found = False
            for row in self.db.execute(cmd):
                dig = row[0]
                url = row[1]
                if found:
                    self.__procTier1Page1(dig, url)
                else:
                    if dig == resumeDig:
                        found = True
                        self.__procTier1Page1(dig, url)

    def execute(self):
        """ entry-url :: t1/pagenation-urls """
        sta, dig, url = self.__queryResumePoint()

        if url is None:
            url = self.entryUrl
        else:
            self.info("resume from:%s" % (url))

        if sta is None or sta == "na" or "paging" == sta:
            self.procPaging(url)
            self.procTier1(None)
            self.procItem(None)

        elif "tier1" == sta:
            self.procTier1(dig)
            self.procItem(None)

        elif "item" == sta:
            self.procItem(dig)

    def quit(self):
        self.db.commit()
        self.db.close()
        self.driver.close()
        self.driver.quit()

def main():
    entryUrl = sys.argv[1]

    tr = TouchRedbook(entryUrl)
    tr.execute()
    tr.quit()

if __name__ == '__main__':
    exit(main())
