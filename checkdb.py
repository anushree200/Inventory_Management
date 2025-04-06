import sqlite3
con = sqlite3.connect("database.db")
cursor = con.cursor()
cursor.execute("SELECT * FROM users")
print(cursor.fetchall())
con.close()
