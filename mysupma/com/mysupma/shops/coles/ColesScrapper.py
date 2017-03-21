import sys

from com.mysupma.shops.WebScrapper import WebScrapper
from com.mysupma.shops.coles.pages import CatPage
from com.mysupma.shops.coles.pages import WelcomePage

# for debug use only
wanted = [
    "https://shop.coles.com.au/a/a-national/everything/browse/bread-bakery/fresh/wraps--pita-flat-bread?pageNumber=1"
    ,
    "https://shop.coles.com.au/a/a-national/everything/browse/bread-bakery/fresh/bread?pageNumber=1"
    , "https://shop.coles.com.au/a/a-national/everything/browse/bread-bakery/fresh?pageNumber=1"
    , "https://shop.coles.com.au/a/a-national/everything/browse/bread-bakery?pageNumber=1"]


class ColesScrapper(WebScrapper):
    def __init__(self, catelogUrl):
        WebScrapper.__init__(self, catelogUrl)
        self.__catelogueUrl = catelogUrl
        self.__entryUrls = [];
        self.driver.get(catelogUrl)

    def scrap(self):
        catUrlMap = self.__buildCatelogue()
        for title in catUrlMap:
            if title == "Tobacco":
                continue
            catUrl = catUrlMap[title]
            self.__processCat1(catUrl, title)

    def __buildCatelogue(self):
        welcomePage = WelcomePage.waitforInstance(self.driver)
        if welcomePage is None:
            print("no found welcome page")
            return
        return welcomePage.getCatUrlMap()

    def quit(self):
        self.driver.quit()
        if self.conn is not None:
            self.conn.close()

    def __processCat1(self, catUrl, title):

        # if catUrl not in wanted: return
        print("processCat1: %s" % catUrl)

        self.driver.get(catUrl)
        catPage = CatPage.waitforInstance(self.driver)
        if catPage is None:
            print("no found such category page")

        subMap = catPage.getCatUrlMap()
        if subMap is None:
            # this is the leaf's page
            self.__updateProductTupleList("coles", title, catUrl, catPage.getProductTuples())
            # done with product on current page but what about next page?
            pageCount = catPage.getPageCount()
            if pageCount < 1:
                # no pagination - no next page
                return
            for i in range(2, pageCount):
                self.__processCatPage1(catUrl, title, i)
            return
        # this is not a leaf - no need parse product on this page
        for key in subMap:
            subCatUrl = subMap[key]
            self.__processCat1(subCatUrl, "%s|%s" % (title, key))

    def __processCatPage1(self, catUrl, title, pageNum):
        if catUrl.endswith("?pageNumber=1"):
            url = catUrl.replace("?pageNumber=1", "?pageNumber=%d" % pageNum)
            print("processPage1:%s" % url)
            self.driver.get(url)
            catPage = CatPage.waitforInstance(self.driver)
            if catPage is None:
                print("no found such category page for page:%s" % pageNum)
                return
            self.__updateProductTupleList("coles", title, url, catPage.getProductTuples())
        else:
            print("unsupport page url:%s" % catUrl)

    def __updateProductTupleList(self, shopName, catTitle, pageUrl, productTupleList):
        """
        output the data into a raw sql insert statement format, refer to
        create table t_raws(
         shop_name varchar(20),
         cat_title varchar(200),
         page_url text,
             prod_brand varchar(64),
             prod_name varchar(64),
             pack_size varchar(20),
         retail_price varchar(10),
         unit_price varchar(30),
         save_price varchar(10),
            img_url text,
            cr_date DATETIME,
         primary key (shop_name, prod_brand, prod_name, pack_size)
        );
        :param shopName: from which the product was found
        :param catTitle: under which category the product was found
        :param pageUrl: at which the product was found
        :param productTupleList: a list of tuple of product
        product in format of (brand, name, size, unitPrice, singlePrice, savedPrice, imgUrl)
        :return: None
        """

        tpl = """insert into t_raws values ("%s", "%s", "%s",    "%s", "%s", "%s",
        "%s", "%s", "%s",    "%s", datetime("now") );\n"""
        for brand, name, size, unitPrice, singlePrice, savedPrice, imgUrl in productTupleList:
            cmd = tpl % (shopName, catTitle, pageUrl,
                         brand, name, size,
                         singlePrice, unitPrice, savedPrice,
                         imgUrl)
            sys.stderr.write(cmd)
