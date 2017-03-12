from com.mysupma.shops.WebScrapper import WebScrapper


class ColesScrapper(WebScrapper):

    def __init__(self, catelogUrl):
        WebScrapper.__init__(self, catelogUrl)
        self.__catelogueUrl = catelogUrl
        self.__entryUrls = []

        self.driver.get(catelogUrl)
        # dismiss welcome dialogue
        el = self.driver.find_element_by_xpath(".//button[@class and contains(text(), 'Start shopping')]")
        el.click()

    def scrap(self):
        if len(self.__entryUrls) < 1:
            self.__buildCatelogue()

    def __buildCatelogue(self):
        xp = ".//h2[contains(text(), 'Browse by category')]"
        pass
