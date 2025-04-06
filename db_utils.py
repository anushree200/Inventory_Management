import sqlite3

def login_user(uname, pwd):
    try:
        con = sqlite3.connect("inventory.db")
        cursor = con.cursor()
        query = f"SELECT * FROM users WHERE username = '{uname}'"
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        con.close()
        if len(records) == 1:
            if pwd == records[0][1]:
                return "Success"
            else:
                return "Incorrect password"
        else:
            return "Please check the username"
    except Exception as e:
        print("Database error:", e)
        return "Database error"

def get_all_products():
    try:
        con = sqlite3.connect("inventory.db")
        cursor = con.cursor()
        cursor.execute("SELECT * FROM products")
        records = cursor.fetchall()
        cursor.close()
        con.close()
        return records
    except:
        return []

def get_user_by_username(uname):
    try:
        con = sqlite3.connect("inventory.db")
        cursor = con.cursor()
        query = f"SELECT * FROM users WHERE username = '{uname}'"
        cursor.execute(query)
        user = cursor.fetchone()
        cursor.close()
        con.close()
        return user
    except Exception as e:
        print("Database error:", e)
        return None

def register_user(username, password, phone):
    try:
        con = sqlite3.connect("inventory.db")
        cursor = con.cursor()

        # Check if user already exists
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            return "Username already exists"

        # Insert new user
        cursor.execute("INSERT INTO users (username, password, phoneno) VALUES (?, ?, ?)", (username, password, phone))
        con.commit()
        con.close()
        return "User registered successfully"
    except Exception as e:
        return f"Database error: {str(e)}"

def get_all_stockmanage():
    try:
        con = sqlite3.connect("inventory.db")
        cursor = con.cursor()
        cursor.execute("SELECT * FROM stock")
        records = cursor.fetchall()
        cursor.close()
        con.close()
        return records
    except:
        return []