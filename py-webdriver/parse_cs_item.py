'''
Created on Sep 18, 2014

@author: Bill
'''
import os
import sys
import sqlite3
import json

DDL = """
create table t_item(
    engine varchar(40),
    body varchar(10),
    title varchar(120),
    
    recordid varchar(40),
    price float,
    odometer int,
    
    state varchar(3),
    href text,
    trans varchar(20),
    
    year int,
    brand varchar(20),
    model varchar(20),
    
    badge varchar(20),
    variant varchar(40),    
    year_cost int,z
    
    kkms_cost int,
    seller varchar(20),    
    cr_date date,
    
    drive_type varchar(10),
    pri_img text,    
    series varchar(40),
    
    offset_price integer,
      
    primary key (recordid)
);

"""

DB_NAME = "cs2.db"

ISQL_TPL = """insert into t_item values (
"%(engine)s",    "%(body)s",     "%(title)s",
"%(recordid)s",   %(price)s,      %(odometer)s,
"%(state)s",     "%(href)s",     "%(trans)s",
%(year)s,      "%(brand)s",    "%(model)s", 
"%(badge)s", "%(variant)s", %(year-cost)s, 
%(kkms-cost)s, "%(seller)s", date('now'), 
"%(drive_type)s", "%(pri-img)s", "%(series)s", 
-1
);
"""

USQL_TPL = """update t_item set
    engine="%(engine)s", body="%(body)s", title="%(title)s",
    price=%(price)s, odometer=%(odometer)s,
    state="%(state)s", href="%(href)s", trans="%(trans)s",
    year = %(year)s, model="%(model)s", brand = "%(brand)s", 
    badge="%(badge)s", variant = "%(variant)s",
    year_cost = %(year-cost)s, kkms_cost = %(kkms-cost)s, 
    seller="%(seller)s", drive_type = "%(drive_type)s",
    cr_date = "%(op_time)s"
    where recordid = "%(recordid)s"
;
"""

YEAR_TODAY = 2014

MAX_AGE = 20
MAX_KKMS = 220


class BrandObj:
    def __init__(self, year, brand, model):
        self.year = year
        self.brand = brand
        self.model = model

        self.badge = None
        self.series = None
        self.variant = None

    @staticmethod
    def _trimPrefix(rest, prefix):
        if rest.startswith(prefix):
            rest = rest[len(prefix):]
        return rest

    @staticmethod
    def _trimSuffix(rest, suffix):
        if rest.endswith(suffix):
            rest = rest[:0 - len(suffix)]
        return rest

    @staticmethod
    def _joinWord(raw, ss):
        rest = raw
        for s in ss:
            replacement = s.replace(" ", "-")
            rest = rest.replace(s, replacement)
        return rest

    @staticmethod
    def _hasStr(rest, ss):
        for s in ss:
            if rest.count(s) > 0:
                return True
        return False

class BrandFord(BrandObj):

    def __init__(self, title, year, brand, model):
        BrandObj.__init__(self, year, brand, model)

        rest = title

        prefix = "%s %s %s" % (year, brand, model)
        rest = self._trimPrefix(rest, prefix)

        rest = self._trimSuffix(rest, "Sports Automatic")
        rest = self._trimSuffix(rest, "Manual")
        rest = rest.strip()

        badges = ["XT", "XR6", "XR8", "G6", "G6E", "Futura", "SR", "ES"]

        rest = self._joinWord(rest, ["FG MkII", "BF Mk II", "BA Mk II"])

        subs = rest.split(" ", 2)
        if 3 == len(subs):
            self.series = subs[0]
            self.badge = subs[1]
            if subs[0] in badges:
                self.series = "na"
                self.badge = subs[0]
                self.variant = "%s %s" % (subs[1], subs[2])
            elif subs[1] in badges:
                self.series = subs[0]
                self.badge = subs[1]
                self.variant = subs[2]
            else:
                self.badge = "na"
                self.variant = "%s %s " % (subs[1], subs[2])
        elif 2 == len(subs):
            if subs[0] in badges:
                self.series = "na"
                self.badge = subs[0]
                self.variant = subs[1]
            elif subs[1] in badges:
                self.series = subs[0]
                self.badge = subs[1]
                self.variant = "na"
            else:
                self.series = "na"
                self.badge = "na"
                self.variant = "%s %s" % (subs[0], subs[1])
        elif 1 == len(subs):
            if subs[0] in badges:
                self.badge = subs[0]
                self.variant = "na"
            else:
                self.badge = "na"
                self.variant = subs[0]
            self.series = "na"
        else:
            print("invalid title for badge:%s" % (rest))

class BrandHolden(BrandObj):

    def __init__(self, title, year, brand, model):
        BrandObj.__init__(self, year, brand, model)

        rest = title

        prefix = "%s %s %s" % (year, brand, model)
        rest = self._trimPrefix(rest, prefix)

        rest = self._trimSuffix(rest, "Sports Automatic")
        rest = self._trimSuffix(rest, "Manual")
        rest = rest.strip()

        badges = ["SS-V", "SS-V-Redline", "SS-V-Z-Series", \
            "SS-Z-Series", "SV6-Z-Series", "Z-Series", \
            "SS", "SV6", "Omega", "International", "Equipe", "Evoke"]

        rest = self._joinWord(rest, ["SS V Redline", "SS V Z Series", "SS V", \
            "SS Z Series", "SV6 Z Series", "Z Series", \
            "VE Series II", "WM Series II", "WH II", \
            " Anniversary", "Special Edition"])

        subs = rest.split(" ", 2)
        if 3 == len(subs):
            if subs[1] in badges:
                self.series = subs[0]
                self.badge = subs[1]
                self.variant = subs[2]
            elif subs[0] in badges:
                self.series = 'na'
                self.badge = subs[0]
                self.variant = "%s %s" % (subs[1], subs[2])
            else:
                self.badge = 'na'
                self.variant = "%s %s" % (subs[1], subs[2])
        elif 2 == len(subs):
            if subs[1] in badges:
                self.series = subs[0]
                self.badge = subs[1]
                self.variant = "na"
            elif subs[0] in badges:
                self.series = 'na'
                self.badge = subs[0]
                self.variant = subs[1]
            else:
                self.series = 'na'
                self.badge = 'na'
                self.variant = "%s %s " % (subs[0], subs[1])
        elif 1 == len(subs):
            self.badge = subs[0]
            self.series = 'na'
            self.variant = 'na'
        else:
            print("invalid title for badge:%s" % (rest))

class CsParser():
    def __init__(self, dbName):
        if os.path.exists(dbName):
            self.db = sqlite3.connect(dbName)
        else:
            self.db = sqlite3.connect(dbName)
            self.db.executescript(DDL)

    def __parseKms(self, raw):
        if raw is None:
            return 0
        buf = ""
        for ch in raw:
            if ch.isdigit():
                buf += ch
            elif ',' == ch:
                continue
            else:
                kkms = int(buf) / 1000
                if kkms <= 0:
                    kkms = 1
                return kkms
        return -1

    def __splitTitle(self, title):
        # Great Wall
        t2 = ["Great Wall", "Land Rover", "th Anniversary", "Alfa Romeo"]
        raw = title
        for phase in t2:
            raw = raw.replace(phase, phase.replace(" ", "-"))

        # 2012 Toyota Camry Altise Sports Automatic
        subs = raw.split(" ", 4)

        if 5 == len(subs):
            year = subs[0]
            brand = subs[1]
            model = subs[2]
            badge = subs[3]
            rest = subs[4]
            return year, brand, model, badge, rest

        elif 4 == len(subs):
            year = subs[0]
            brand = subs[1]
            model = subs[2]
            badge = subs[3]
            return year, brand, model, badge, "na"

        elif 3 == len(subs):
            year = subs[0]
            brand = subs[1]
            model = subs[2]
            return year, brand, model, "na", "na"
        return None, None, None, None, None

    def __buildCost(self, jsMap):
        yearBuild = int(jsMap["year"])
        price = jsMap["price"]
        # kms
        kkms = jsMap["odometer"]
        yearRemain = MAX_AGE - (YEAR_TODAY - yearBuild)
        kkmsRemain = MAX_KKMS - kkms
        if kkmsRemain <= 0:
            kkmsRemain = 1
        if yearRemain <= 0:
            yearRemain = 1

        yearCost = int(price / yearRemain)
        kkmsCost = int(price / kkmsRemain)

        return yearCost, kkmsCost


    def __buildSeller(self, jsMap):
        href = jsMap["href"]
        items = href.split('/')
        if len(items) > 4:
            return items[3]
        return "na"

    def proc1(self, fp):
        # print(fp)
        with open(fp, "r") as f:
            jsMap = json.load(f)
            kms = self.__parseKms(jsMap["odometer"])
            if jsMap["state"] is None:
                jsMap["state"] = "na"

            if jsMap["price"] is None:
                jsMap["price"] = 0
            else:
                jsMap["price"] = int(float(jsMap["price"]))

            year, brand, model, badge, variant = self.__splitTitle(jsMap["title"])
            if year is None:
                print("invalid title:%s" % (jsMap["title"]))
                return
            else:
                jsMap["year"] = int(year)
                jsMap["brand"] = brand
                jsMap["model"] = model
                jsMap["badge"] = badge
                jsMap["variant"] = variant
                jsMap["series"] = 'na'

            jsMap["op_time"] = jsMap["op_time"].split(' ')[0]

            if kms < 0:
                print(fp)
                print(kms)
            else:
                jsMap["odometer"] = kms

                yearCost, kkmsCost = self.__buildCost(jsMap)
                jsMap["year-cost"] = yearCost
                jsMap["kkms-cost"] = kkmsCost

                jsMap["seller"] = self.__buildSeller(jsMap)

                cmd = "na"
                try:
                    cmd = ISQL_TPL % jsMap
                    self.db.execute(cmd)
                except sqlite3.IntegrityError:
                    cmd = USQL_TPL % jsMap
                    try:
                        self.db.execute(cmd)
                    except sqlite3.OperationalError as e:
                        print(fp)
                        print(cmd)
                        print(e)
                except sqlite3.OperationalError as e:
                    print(fp)
                    print(cmd)
                    print(e)

    def __fixTitle(self):
        # fix ford title
        cmd = "select recordid, year, brand, model, title from t_item where brand in ('Ford', 'Holden') "
        for row in self.db.execute(cmd):
            recId = row[0]
            year = str(row[1])
            brand = row[2]
            model = row[3]
            title = row[4]

            if "Ford" == brand and "Falcon" == model:
                bf = BrandFord(title, year, brand, model)
            elif "Holden" == brand and "Commodore" == model:
                bf = BrandHolden(title, year, brand, model)

            ucmd = "update t_item set badge = '%s', series = '%s', variant = '%s' where recordid = '%s' " \
                % (bf.badge, bf.series, bf.variant, recId)
            self.db.execute(ucmd)

        self.db.commit()

    def __fixOffsetPrice(self):
        self.db.execute("update t_item set offset_price = 9000")
        
        cmd = "select low_trade, build_year, brand, model, badge, serie from t_price_guide "

        ucmd = """ update t_item set offset_price = price - %s where year = %s
            and brand = "%s" and model = "%s" and badge = "%s"
            and series = "%s" """
            
        for row in self.db.execute(cmd):
            low = row[0]
            year = row[1]
            brand = row[2]
            model = row[3]
            badge = row[4]
            serie = row[5]

            ucmd1 = ucmd % (low, year, brand, model, badge, serie)
            # print(ucmd1)
            self.db.execute(ucmd1)

        self.db.commit()

    def __afterWork(self):
        self.__fixTitle()
        self.__fixOffsetPrice()

        print('update ford holden')

    def procDir(self, inputDir):
        for dirName, dirNames, fileNames in os.walk(inputDir):
            for name in fileNames:
                firstName, extName = os.path.splitext(name)
                if ".json" == extName:
                    fp = os.path.join(dirName, name)
                    self.proc1(fp)
                    # return
            self.db.commit()
            sys.stderr.write('.')

        self.__afterWork()

    def close(self):
        self.db.close()

def main():
    dbName = sys.argv[1]
    inputDir = sys.argv[2]
    pc = CsParser(dbName)
    pc.procDir(inputDir)
    pc.close()


if __name__ == '__main__':
    exit(main())
