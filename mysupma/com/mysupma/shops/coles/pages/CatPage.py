import selenium
from com.mysupma.shops.GenericPage import GenericPage, waitforXpath


class CatPage(GenericPage):

    def getProductTuples(self):
        """
        Return a tuple of (brand, name, size, unitPrice, singlePrice, savedPrice, imgUrl)
        :return:
        """
        cellXp = ".//div[@class='product-padding']"
        cells = self.findElements(cellXp)
        print("found %d cell/s" % (len(cells)))
        pending = []
        for cell in cells:
            brand = self.__extractChildText(cell, ".//span[@class='product-brand']")
            name = self.__extractChildText(cell, ".//span[@class='product-name']")
            size = self.__extractChildText(cell, ".//span[@class='package-size']", "0")
            unitPrice = self.__extractChildText(cell, ".//span[@class='package-price']")
            singlePrice = self.__extractChildText(cell, ".//strong[@class='product-price']")
            savedPrice = self.__extractChildText(cell, ".//span[@class='product-saving']/strong", "0")
            imgUrl = self.__extractChildAttr(cell, ".//div[@class='product-image']/a/img", "src")
            pending.append((brand, name, size, unitPrice, singlePrice, savedPrice, imgUrl))
        return pending

    def getCatUrlMap(self):
        """
        Build a dictionary of title:url
        :return:
        """
        ret = dict()
        xp = ".//div[@id='cat-nav-items']//li/a"
        anchors = self.findElements(xp)
        anchorCount = len(anchors)
        print("found %d anchor/s of cat-nav-items" % (anchorCount))
        if anchorCount < 1:
            return None
        for anchor in anchors:
            href = anchor.get_attribute("href")
            el = anchor.find_element_by_xpath(".//span[@class='item-title']")
            title = el.text
            ret[title] = href
        return ret

    def getPageCount(self):
        xp = ".//ul[@class='pagination']/li[@class='page-number']"
        els = self.findElements(xp)
        return len(els)

    def __extractChildText(self, cell, xp, defaultValue=None):
        try:
            el = cell.find_element_by_xpath(xp)
            if el is None:
                return defaultValue
        except selenium.common.exceptions.NoSuchElementException:
            return defaultValue
        return el.text

    def __extractChildAttr(self, cell, xp, attrName):
        try:
            el = cell.find_element_by_xpath(xp)
            if el is None:
                return None
        except selenium.common.exceptions.NoSuchElementException:
            return None
        attr = el.get_attribute(attrName)
        if attr is None:
            return None
        return attr


def waitforInstance(driver):
    xp = ".//a[@id='cat-nav-back']"
    if waitforXpath(driver, xp):
        return CatPage(driver)
    return None