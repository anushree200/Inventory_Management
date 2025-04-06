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
        con = sqlite3.connect("database.db")
        cursor = con.cursor()
        cursor.execute("select * from products")
        records = cursor.fetchall()
        cursor.close()
        con.close()
        return records
    except:
        return []