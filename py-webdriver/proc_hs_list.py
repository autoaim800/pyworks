import os
import sys
from py_sel import PySel
import sqlite3

DB_NAME = "hs2.db"
DB_DDL = """
create table t_streets(
st_state varchar(3),
st_city varchar(40),
st_zip varchar(4),
st_name varchar(40),
min_num integer,
max_num integer,
primary key(st_state, st_city, st_name)
);

"""
LOOP_MAX = 6000

class ProcHsList(PySel):

    def __init__(self):
        self.driver = self.buildDriver()
        existFlag = os.path.exists(DB_NAME)
        self.db = sqlite3.connect(DB_NAME)

        if not existFlag:
            self.db.executescript(DB_DDL)

    def setEntry(self, url):
        pass

    def __procOne(self):
        pass

    def __pushAddress(self, addrList):
        pass

    def execute(self):
        # TBD
        for i in range(LOOP_MAX):
            nextNode, addresses = self.__procOne()
            if nextNode is None:
                break
            # TBD
            self.__pushAddress(addresses)

    def destroy(self):
        if self.driver is not None:
            self.driver.close()
            self.driver.quit()
            self.driver = None

        if self.db is not None:
            self.db.close()
            self.db = None


def main():
    pl = ProcHsList()
    for url in sys.argv[1:]:
        if url.startswith('@'):
            fp = url[1:]
            lines = []
            with open(fp, "r") as f:
                lines = f.readlines()
            if len(lines) > 0:
                for line in lines:
                    ln = line.strip()
                    if ln.startswith('#'):
                        continue
                    if len(ln) < 1:
                        continue
                    pl.setEntry(ln)
                    pl.execute()
        else:
            pl.setEntry(url)
            pl.execute()
    pl.destroy()

if __name__ == '__main__':
    exit(main())
