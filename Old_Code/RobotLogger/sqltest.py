import MySQLdb

conn = MySQLdb.connect (host = "134.139.125.220",
                           user = "rhx",
                           passwd = "rhx",
                           db = "rhx")
cursor = conn.cursor ()
cursor.execute ("SELECT VERSION()")
row = cursor.fetchone ()
print "server version:", row[0]
cursor.close ()
conn.close ()