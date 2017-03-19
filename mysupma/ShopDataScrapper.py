from com.mysupma.shops.coles.ColesScrapper import ColesScrapper
from com.mysupma.shops.woolies.WooliesScrapper import WooliesScrapper


class ShopDataScrapper:
    def scrap(self):
        cs = ColesScrapper("https://shop.coles.com.au/a/a-national/everything/browse")
        cs.scrap()
        cs.quit()
        # ws = WooliesScrapper("https://www.woolworths.com.au/")
        # cs.scrap()


def main():
    sds = ShopDataScrapper()
    sds.scrap()


if __name__ == "__main__":
    exit(main())
