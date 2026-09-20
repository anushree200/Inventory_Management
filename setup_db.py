import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "inventory.db")

def init_db():
    con = sqlite3.connect(DB_PATH)
    cursor = con.cursor()

    # Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phoneno TEXT,
            role TEXT DEFAULT 'staff'
        )
    """)

    # Products Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            pid INTEGER PRIMARY KEY AUTOINCREMENT,
            pname TEXT UNIQUE NOT NULL,
            category TEXT,
            size INTEGER,
            qty INTEGER NOT NULL DEFAULT 0,
            minqty INTEGER NOT NULL DEFAULT 0,
            price INTEGER NOT NULL DEFAULT 0,
            barcode TEXT UNIQUE
        )
    """)

    # Vendor Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendor (
            vendorid INTEGER PRIMARY KEY,
            pid INTEGER,
            pname TEXT,
            vendorname TEXT,
            contactno TEXT,
            email TEXT,
            address TEXT
        )
    """)

    # Unified Stock / Sales History Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock (
            saleid INTEGER PRIMARY KEY AUTOINCREMENT,
            pid INTEGER,
            pname TEXT,
            qty_sold INTEGER NOT NULL,
            qty_remaining INTEGER NOT NULL,
            sale_date TEXT NOT NULL
        )
    """)

    con.commit()
    con.close()
    print("Database tables initialized successfully.")

if __name__ == "__main__":
    init_db()