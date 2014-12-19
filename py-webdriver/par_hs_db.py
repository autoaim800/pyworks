'''
Created on 15 Oct 2014

'''
import os
import sys
import sqlite3
import re

DDL = """
create table t_addr1(
    
    st_state varchar(20),
    st_city varchar(40),
    st_zip varchar(10),
    
    st_name varchar(40),
    street_num integer,
    unit_num integer,
    
    primary key (st_state, st_city, st_name)
);
"""

class StreetObj:
    ITPL = """insert into t_addr1 values (
        "%(state)s", "%(city)s",  "%(zip)s", 
        "%(name)s", %(street-num)s, %(unit-num)s );"""
    def __init__(self):
        self.state = None
        self.city = None
        self.zip = None
        self.name = None
        self.streetNum = 0
        self.unitNum = 0

    def __build(self):
        self.boundle = {"state":self.state, "city":self.city, "zip":self.zip, \
                        "name":self.name, "street-num":self.streetNum, \
                        "unit-num":self.unitNum}

    def toisql(self):
        self.__build()
        return self.ITPL % self.boundle

class HsParser(object):

    def __init__(self, dbName):
        self.db = sqlite3.connect(dbName)

    def __buildStreetObject1(self, raw):
        streetAddr, cityName, stateName, zipCode = self.__splitAddr4(raw)
        if streetAddr is not None:
            subs = streetAddr.split(' ', 1)
            if 2 == len(subs):
                streetName = subs[1]
                streetNum = subs[0]
                so = StreetObj()
                so.name = streetName
                so.streetNum = int(streetNum)
                so.unitNum = 0
                so.city = cityName
                so.state = stateName
                so.zip = int(zipCode)
                return so
        return None

    def __leadingDigitOnly(self, raw):
        buf = ""
        for ch in raw:
            if ch.isdigit():
                buf += ch
            else:
                break
        return buf

    def __buildStreetObject2(self, raw):
        # 3B Culgoa Street, Sunshine Beach, QLD 4567
        streetAddr, cityName, stateName, zipCode = self.__splitAddr4(raw)
        if streetAddr is not None:
            subs = streetAddr.split(' ', 1)
            if 2 == len(subs):
                streetName = subs[1]
                streetNum = subs[0]
                streetNum = self.__leadingDigitOnly(streetNum)

                so = StreetObj()
                so.name = streetName
                so.streetNum = int(streetNum)
                so.unitNum = 0
                so.city = cityName
                so.state = stateName
                so.zip = int(zipCode)
                return so
        return None

    def __buildStreetObject3(self, raw):
        # 100/3 Culgoa Street, Sunshine Beach, QLD 4567
        streetAddr, cityName, stateName, zipCode = self.__splitAddr4(raw)
        if streetAddr is not None:
            subs = streetAddr.split(' ', 1)
            if 2 == len(subs):
                streetName = subs[1]
                ss = subs[0].split('/', 1)

                if 2 == len(ss):
                    so = StreetObj()
                    so.name = streetName
                    so.streetNum = int(ss[1])
                    so.unitNum = int(ss[0])
                    so.city = cityName
                    so.state = stateName
                    so.zip = int(zipCode)
                    return so
        return None

    def __buildStreetObject4(self, raw):
        # 100/3B Culgoa Street, Sunshine Beach, QLD 4567
        streetAddr, cityName, stateName, zipCode = self.__splitAddr4(raw)
        if streetAddr is not None:
            subs = streetAddr.split(' ', 1)
            if 2 == len(subs):
                streetName = subs[1]
                ss = subs[0].split('/', 1)

                if 2 == len(ss):
                    so = StreetObj()
                    so.name = streetName
                    so.streetNum = int(self.__leadingDigitOnly(ss[1]))
                    so.unitNum = int(ss[0])
                    so.city = cityName
                    so.state = stateName
                    so.zip = int(zipCode)
                    return so
        return None
    def __splitAddr4(self, raw):
        # 3 Culgoa Street, Sunshine Beach, QLD 4567
        items = raw.split(',')
        if 3 == len(items):
            subs = items[2].strip().split(' ')
            if 2 == len(subs):
                return items[0].strip(), items[1].strip(), \
                    subs[0].strip(), subs[1].strip()
        return None, None, None, None


    def __parseInt(self, raw):
        try:
            return int(raw)
        except ValueError as e:
            print(str(e))
            print(raw)
            return -1

    def _buildStreetObj(self, raw):
        
        raw = raw.replace(" /", "/").replace("/ ", "/")\
            .replace(" -", "-").replace("- ", "-")\
            .replace('.', '')
            
        reStateZip = "\s[A-Z]+\s\d+$"
        reCityName = "\s[a-zA-Z \-]+"
        reStreetName = "\s[a-zA-Z ]+"
        
        reBoundle = {"re-street-name":reStreetName, "re-city-name":reCityName, \
                     "re-state-zip":reStateZip}

        exp0 = r"\d+%(re-street-name)s,%(re-city-name)s,%(re-state-zip)s" % reBoundle

        # 3 Culgoa Street, Sunshine Beach, QLD 4567
        exp1 = r"^\d+%(re-street-name)s,%(re-city-name)s,%(re-state-zip)s" % reBoundle

        # 3B Culgoa Street, Sunshine Beach, QLD 4567
        exp2 = r"^\d+[a-zA-Z]%(re-street-name)s,%(re-city-name)s,%(re-state-zip)s" % reBoundle

        # 100/3 Culgoa Street, Sunshine Beach, QLD 4567
        exp3 = r"^\d+/\d+%(re-street-name)s,%(re-city-name)s,%(re-state-zip)s" % reBoundle

        # 100/3B Culgoa Street, Sunshine Beach, QLD 4567
        exp4 = r"^\d+/\d+[a-zA-Z]%(re-street-name)s,%(re-city-name)s,%(re-state-zip)s" % reBoundle

        # 1-3 Culgoa Street, Sunshine Beach, QLD 4567
        exp5 = r"^\d+-\d+%(re-street-name)s,%(re-city-name)s,%(re-state-zip)s" % reBoundle
        
        # Unit 10/28 Viewland Drive, Noosa Heads, QLD 4567
        exp6 = r"^[a-zA-Z]+\s\d+/\d+%(re-street-name)s,%(re-city-name)s,%(re-state-zip)s" % reBoundle
        
        # 10/5-28 Viewland Drive, Noosa Heads, QLD 4567
        exp7 = r"^\d+/\d+-\d+%(re-street-name)s,%(re-city-name)s,%(re-state-zip)s" % reBoundle
        
        # 10C/28 Viewland Drive, Noosa Heads, QLD 4567
        exp8 = r"^[a-zA-Z0-9]+/\d+%(re-street-name)s,%(re-city-name)s,%(re-state-zip)s" % reBoundle
        
        # 1-5/28 Viewland Drive, Noosa Heads, QLD 4567
        exp9 = r"^\d+-\d+/\d+%(re-street-name)s,%(re-city-name)s,%(re-state-zip)s" % reBoundle
        
        # 10i/5-28 Viewland Drive, Noosa Heads, QLD 4567
        exp10 = r"^[a-zA-Z0-9]+/\d+-\d+%(re-street-name)s,%(re-city-name)s,%(re-state-zip)s" % reBoundle
        
        regex0 = re.compile(exp0)
        regex1 = re.compile(exp1)
        regex2 = re.compile(exp2)
        regex3 = re.compile(exp3)
        regex4 = re.compile(exp4)
        regex5 = re.compile(exp5)
        regex6 = re.compile(exp6)
        regex7 = re.compile(exp7)
        regex8 = re.compile(exp8)
        regex9 = re.compile(exp9)
        regex10 = re.compile(exp10)
        
        ret = regex1.findall(raw)
        if ret is not None and len(ret) > 0:
            return self.__buildStreetObject1(ret[0])
        ret = regex2.findall(raw)
        if ret is not None and len(ret) > 0:
            return self.__buildStreetObject2(ret[0])
        ret = regex3.findall(raw)
        if ret is not None and len(ret) > 0:
            return self.__buildStreetObject3(ret[0])
        ret = regex4.findall(raw)
        if ret is not None and len(ret) > 0:
            return self.__buildStreetObject4(ret[0])

        ret = regex5.findall(raw)
        if ret is not None and len(ret) > 0:
            ret = regex0.findall(raw)
            return self.__buildStreetObject1(ret[0])
        
        ret = regex6.findall(raw)
        if ret is not None and len(ret) > 0:
            ret = regex0.findall(raw)
            return self.__buildStreetObject1(ret[0])
        
        ret = regex7.findall(raw)
        if ret is not None and len(ret) > 0:
            ret = regex0.findall(raw)
            return self.__buildStreetObject1(ret[0])
        
        ret = regex8.findall(raw)
        if ret is not None and len(ret) > 0:
            ret = regex0.findall(raw)
            return self.__buildStreetObject1(ret[0])

        ret = regex9.findall(raw)
        if ret is not None and len(ret) > 0:
            ret = regex0.findall(raw)
            return self.__buildStreetObject1(ret[0])

        ret = regex10.findall(raw)
        if ret is not None and len(ret) > 0:
            ret = regex0.findall(raw)
            return self.__buildStreetObject1(ret[0])
        
        return None

    def walk(self):
        cmd = """select hs_id, hs_addr 
            from t_addrs 
            where flag = 'N' limit 1000 """
        for i in range(100):
            pending = []
            failed = []
            rowCount = 0
            for row in self.db.execute(cmd):
                hsId = row[0]
                hsAddr = row[1]
                so = self._buildStreetObj(hsAddr)
                if so is None:
                    # print("%s=%s" % (so, hsAddr))
                    failed.append(hsId)
                else:
                    pending.append((hsId, so))
                rowCount += 1
            if rowCount < 1:
                return
            for hsId, so in pending:
                ucmd = "update t_addrs set flag='Y' where hs_id = \"%s\" " % (hsId)
                try:
                    self.db.execute(so.toisql())
                    self.db.execute(ucmd)
                except sqlite3.IntegrityError as e:
                    ucmd = "update t_addrs set flag='M' where hs_id = \"%s\" " % (hsId)
                    self.db.execute(ucmd)
            for hsId in failed:
                ucmd = "update t_addrs set flag='F' where hs_id = \"%s\" " % (hsId)
                self.db.execute(ucmd)
            self.db.commit()
            sys.stdout.write('.')

    def close(self):
        if self.db is not None:
            self.db.close()
            self.db = None

def main():
    dbName = sys.argv[1]
    hp = HsParser(dbName)
    hp.walk()
    hp.close()

if __name__ == '__main__':
    exit(main())
