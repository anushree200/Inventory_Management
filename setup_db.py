import sqlite3

conn = sqlite3.connect("inventory.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL
)
''')

cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "admin123"))

cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    pid INTEGER PRIMARY KEY AUTOINCREMENT,
    pname TEXT NOT NULL,
    qty INTEGER NOT NULL,
    price INTEGER NOT NULL
)
''')

conn.commit()
conn.close()
print("Database and tables created successfully.")
