from com.mysupma.shops.WebScrapper import WebScrapper
from com.mysupma.shops.coles.pages import CatPage
from com.mysupma.shops.coles.pages import WelcomePage


class ColesScrapper(WebScrapper):

    def __init__(self, catelogUrl):
        WebScrapper.__init__(self, catelogUrl)
        self.__catelogueUrl = catelogUrl
        self.__entryUrls = []

        self.driver.get(catelogUrl)

    def scrap(self):
        catUrlMap = self.__buildCatelogue()
        for title in catUrlMap:
            if title == "Tobacco":
                continue
            catUrl = catUrlMap[title]
            self.__processCat1(catUrl, title)
            break

    def __buildCatelogue(self):
        welcomePage = WelcomePage.waitforInstance(self.driver)
        if welcomePage is None:
            print("no found welcome page")
            return
        return welcomePage.getCatUrlMap()

    def quit(self):
        self.driver.quit()

    def __processCat1(self, catUrl, title):
        self.driver.get(catUrl)
        catPage = CatPage.waitforInstance(self.driver)
        if catPage is None:
            print("no found such category page")

        subMap = catPage.getCatUrlMap()
        if subMap is None:
            # this is the leaf's page
            print("coles: %s" % title)
            print(catPage.getProductTuples())
            pageCount = catPage.getPageCount()
            if pageCount < 1:
                # no pagination
                return
            for i in range(2, pageCount):
                self.__processCatPage1(catUrl, title, i)
            return

        for key in subMap:
            subCatUrl = subMap[key]
            self.__processCat1(subCatUrl, "%s|%s" % (title, key))

    def __processCatPage1(self, catUrl, title, pageNum):
        pass

