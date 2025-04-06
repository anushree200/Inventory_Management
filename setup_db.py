import sqlite3

conn = sqlite3.connect("inventory.db")
cursor = conn.cursor()

# Users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    phoneno INTEGER
)
''')

# Insert demo user
cursor.execute("INSERT OR IGNORE INTO users (username, password, phoneno) VALUES (?, ?, ?)", ("anu", "anu123", 8939596811))

# Products table
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    pid INTEGER PRIMARY KEY AUTOINCREMENT,
    pname TEXT NOT NULL,
    category TEXT,
    size INTEGER,
    qty INTEGER NOT NULL,
    minqty INTEGER NOT NULL,
    price INTEGER NOT NULL,
    barcode INTEGER NOT NULL
)
''')

# Vendor table
cursor.execute('''
CREATE TABLE IF NOT EXISTS vendor(
    pid INTEGER PRIMARY KEY,
    pname TEXT NOT NULL,
    vendorid INTEGER NOT NULL,
    vendorname TEXT,
    contactno INTEGER,
    email TEXT,
    address TEXT
)
''')

# Stock table
cursor.execute('''
CREATE TABLE IF NOT EXISTS stock(
    vendorid INTEGER PRIMARY KEY,
    vendorname TEXT,
    pid INTEGER NOT NULL,
    pname TEXT,
    sellingprice INTEGER,
    stockeddate DATE,
    restockingdate DATE,
    expirationdate DATE,
    qntypresent INTEGER,
    qntysold INTEGER,
    description TEXT
)
''')

conn.commit()
conn.close()
print("Database and tables created successfully.")
