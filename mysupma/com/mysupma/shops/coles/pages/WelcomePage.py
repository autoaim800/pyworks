from com.mysupma.shops.GenericPage import GenericPage, waitforXpath
from com.mysupma.shops.coles.pages.CatPage import CatPage


class WelcomePage(GenericPage):
    def __init__(self, webdriver):
        GenericPage.__init__(self, webdriver)

    def getCatUrlMap(self):
        """
        Build a dictionary of title:url
        :return:
        """
        ret = dict()
        xp = ".//div[@id='cat-nav-list-1']//li/a"
        anchors = self.findElements(xp)
        print("found %d anchor/s at welcome" % (len(anchors)))
        for anchor in anchors:
            href = anchor.get_attribute("href")
            el = anchor.find_element_by_xpath(".//span[@class='item-title']")
            title = el.text
            ret[title] = href
        return ret

def waitforInstance(driver):

    xp1 = ".//button[@class and contains(text(), 'Start shopping')]"
    startButton = waitforXpath(driver, xp1)
    if startButton is None:
        print("no found Start shopping button")
    startButton.click()

    xp = ".//h2[contains(text(), 'Browse by category')]"
    if waitforXpath(driver, xp):
        return WelcomePage(driver)
    return None
