import sqlite3
con = sqlite3.connect("inventory.db")
cursor = con.cursor()
cursor.execute("SELECT * FROM vendor")
print(cursor.fetchall())
con.close()
