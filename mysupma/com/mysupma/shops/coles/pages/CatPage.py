from com.mysupma.shops.GenericPage import GenericPage, waitforXpath


class CatPage(GenericPage):

    def getProductTuples(self):
        """
        Return a tuple of (brand, name, pack-size, pack-price)
        :return:
        """
        cellXp = ".//div[@class='product-padding']"
        cells = self.findElements(cellXp)
        print("found %d cell/s" % (len(cells)))
        for cell in cells:
            brand = cell.find_element_by_xpath(".//span[@class='product-brand']").text
            name = cell.find_element_by_xpath(".//span[@class='product-name']").text
            size = cell.find_element_by_xpath(".//span[@class='package-size']").text
            price = cell.find_element_by_xpath(".//span[@class='package-price']").text
            print("coles: %s|%s|%s|%s" % (brand, name, size, price))
        return "getProductTuples() return"

    def getCatUrlMap(self):
        """
        Build a dictionary of title:url
        :return:
        """
        ret = dict()
        xp = ".//div[@id='cat-nav-items']//li/a"
        anchors = self.findElements(xp)
        anchorCount = len(anchors)
        print("found %d anchor/s" % (anchorCount))
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


def waitforInstance(driver):
    xp = ".//a[@id='cat-nav-back']"
    if waitforXpath(driver, xp):
        return CatPage(driver)
    return None