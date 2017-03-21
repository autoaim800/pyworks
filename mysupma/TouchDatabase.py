import os
import sqlite3
dbFp = "mysupma1.db"
if not os.path.exists(dbFp):
    conn = sqlite3.connect(dbFp)

    body = None
    with open ("mysupma1.sql") as f:
        body = f.read()

    if body is not None:
        subs = body.split(";")
        for sub in subs:
            cmd = "%s;" % sub
            print(cmd)
            conn.execute(cmd)
            conn.commit()
    conn.close()