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
    
# For search/filter/sort in products.html

def search_products_by_name(keyword):
    try:
        con = sqlite3.connect("inventory.db")
        cursor = con.cursor()
        query = f"SELECT * FROM products WHERE pname LIKE ?"
        cursor.execute(query, ('%' + keyword + '%',))
        records = cursor.fetchall()
        con.close()
        return records
    except:
        return []

def get_products_sorted(sort_by="qty", order="asc"):
    try:
        con = sqlite3.connect("inventory.db")
        cursor = con.cursor()
        if sort_by not in ("qty", "price"): sort_by = "qty"
        if order not in ("asc", "desc"): order = "asc"
        cursor.execute(f"SELECT * FROM products ORDER BY {sort_by} {order}")
        records = cursor.fetchall()
        con.close()
        return records
    except:
        return []

def get_products_grouped_by_category():
    try:
        con = sqlite3.connect("inventory.db")
        cursor = con.cursor()
        cursor.execute("SELECT category, GROUP_CONCAT(pname || ' (Qty: ' || qty || ')') FROM products GROUP BY category")
        records = cursor.fetchall()
        con.close()
        return records
    except:
        return []

# For modify_inventory.html

def add_product(data):
    try:
        con = sqlite3.connect("inventory.db")
        cursor = con.cursor()
        cursor.execute("""
            INSERT INTO products (pname, category, size, qty, minqty, price, barcode)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (data['pname'], data['category'], data['size'], data['qty'],
              data['minqty'], data['price'], data['barcode']))
        con.commit()
        con.close()
        return "Product added successfully"
    except Exception as e:
        return f"Error: {e}"

def delete_product_by_name(pname):
    try:
        con = sqlite3.connect("inventory.db")
        cursor = con.cursor()
        cursor.execute("DELETE FROM products WHERE pname = ?", (pname,))
        con.commit()
        con.close()
        return "Product deleted successfully"
    except Exception as e:
        return f"Error: {e}"

def update_product(pname, field, new_value):
    try:
        if field not in ("qty", "price","size"):
            return "Invalid field"
        con = sqlite3.connect("inventory.db")
        cursor = con.cursor()
        query = f"UPDATE products SET {field} = ? WHERE pname = ?"
        cursor.execute(query, (new_value, pname))
        con.commit()
        con.close()
        return "Product updated successfully"
    except Exception as e:
        return f"Error: {e}"
def update_product_quantity(barcode_data,delta):
    con = sqlite3.connect("inventory.db")
    cursor = con.cursor()
    cursor.execute("SELECT qty FROM products WHERE barcode = ?", (barcode_data,))
    row = cursor.fetchone()
    current_qty = row[0]
    new_qty = current_qty + delta
    cursor.execute("UPDATE products SET qty = ? WHERE barcode = ?", (new_qty, barcode_data))
    con.commit()
    con.close()
    return f"Product quantity updated to {new_qty}"
def update_qty_one(pname):
    con = sqlite3.connect("inventory.db")
    cursor = con.cursor()
    cursor.execute("SELECT qty FROM products WHERE pname = ?", (pname,))
    row = cursor.fetchone()
    current_qty = row[0]
    new_qty = current_qty - 1
    cursor.execute("UPDATE products SET qty = ? WHERE pname = ?", (new_qty, pname))
    con.commit()
    con.close()
    return f"user bought {pname}"