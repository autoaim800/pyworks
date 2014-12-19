'''
Created on Dec 9, 2014

'''

import os
import sys
import sqlite3
from xlsx_cs_item import HEADERS_ROW
from jinja2 import Template

TPL = """
<html><body>
<table>
<tr>
<td>#</td>
<td>title</td>
<td>price</td>
<td>offset</td>
<td>kkms</td>
<td>kkms-cost</td>
<td>year</td>
<td>year-cost</td>
<td>engine</td>
<td>state</td>
<td>dealer/private</td>
</tr>
{% for item in items %}
<tr>
<td><a href="{{ item.href }}" target="_blank"><img src="images/{{item.recordid}}.jpg" /></a></td>
<td>{{ item.title }}</td>
<td>${{ item.offset_price }}</td>
<td>${{ item.price }}</td>
<td>{{ item.odometer }}kkm</td>
<td>${{ item.kkms_cost }}</td>
<td>Y{{ item.year }}</td>
<td>${{ item.year_cost }}</td>
<td>{{ item.engine }}</td>
<td>{{ item.state }}</td>
<td>{{ item.seller }}</td>
</tr>
{% endfor %}
</table>
</body>
</html>
"""

QSQL_CMD = """ select *
from t_item
where price > 0 and kkms_cost > 0 and year >=2003
    and brand = '%s' and model = '%s' and cr_date = '%s'
    and state = 'QLD'
order by offset_price
"""

def writef(outfp, raw):
    with open(outfp, 'w') as f:
        f.write(raw)

class HtmlCs(object):

    def __init__(self, dbFp):
        self.db = sqlite3.connect(dbFp)

    def closeDb(self):
        self.db.close()

    def __queryStr1(self, cmd):
        for row in self.db.execute(cmd):
            return row[0]
        return None

    def __writeFor(self, outDir, brand, model, crDate):

        outfp = os.path.join(outDir, "%s-%s-%s.html" % (brand, model, crDate))
        cmdfp = os.path.join(outDir, "%s-%s-%s.cmd" % (brand, model, crDate))

        cmd = QSQL_CMD % (brand, model, crDate)

        pending = []
        idUrls = []
        for row in self.db.execute(cmd):
            boundle = dict()
            for head, index in HEADERS_ROW:
                boundle[head.replace("-", "_")] = row[index]
            pending.append(boundle)
            if "na" != boundle["pri_img"]:
                idUrls.append((boundle["recordid"], boundle["pri_img"]))
        template = Template(TPL)
        writef(outfp, template.render(items=pending))

        tmp = ""
        for recid, href in idUrls:
            imgfp = "images/%s.jpg" % (recid)
            if not os.path.exists(imgfp):
                tmp += "wget -O %s \"%s\"\n" % (imgfp, href)
        writef(cmdfp, tmp)

    def writeTo(self, outDir):
        # last date
        lastDate = self.__queryStr1("select distinct cr_date from t_item order by 1 desc limit 1")
        self.__writeFor(outDir, "Ford", "Falcon", lastDate)
        self.__writeFor(outDir, "Holden", "Commodore", lastDate)


def main():
    dbFp = sys.argv[1]
    outFp = sys.argv[2]

    hc = HtmlCs(dbFp)
    hc.writeTo(os.getcwd())
    hc.closeDb()

if __name__ == '__main__':
    exit(main())
