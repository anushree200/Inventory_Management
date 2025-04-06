import sqlite3

conn = sqlite3.connect("inventory.db")
cursor = conn.cursor()

# Users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL
)
''')

# Insert demo user
cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ("admin", "admin123"))

# Products table
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    pid INTEGER PRIMARY KEY AUTOINCREMENT,
    pname TEXT NOT NULL,
    category TEXT,
    description TEXT,
    qty INTEGER NOT NULL,
    price INTEGER NOT NULL,
    supplier TEXT,
    date_added TEXT,
    image TEXT,
    status TEXT
)
''')

conn.commit()
conn.close()
print("Database and tables created successfully.")
