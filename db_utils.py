import datetime
import os
import sqlite3
from pathlib import Path

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "inventory.db")
ph = PasswordHasher()


def connect_db():
    return sqlite3.connect(DB_PATH)


def _is_argon2_hash(value):
    return isinstance(value, str) and value.startswith("$argon2")


def login_user(uname, pwd):
    try:
        con = connect_db()
        cursor = con.cursor()
        cursor.execute("SELECT password, role FROM users WHERE username = ?", (uname,))
        record = cursor.fetchone()
        cursor.close()
        con.close()
        if record is None:
            return {"status": "error", "message": "Please check the username"}

        stored_hash, role = record[0], record[1]

        if _is_argon2_hash(stored_hash):
            try:
                if ph.verify(stored_hash, pwd):
                    return {"status": "success", "role": role}
                return {"status": "error", "message": "Incorrect password"}
            except (VerifyMismatchError, VerificationError):
                return {"status": "error", "message": "Incorrect password"}

        if stored_hash == pwd:
            try:
                con = connect_db()
                cursor = con.cursor()
                cursor.execute(
                    "UPDATE users SET password = ? WHERE username = ?",
                    (ph.hash(pwd), uname)
                )
                con.commit()
                cursor.close()
                con.close()
            except Exception:
                pass
            return {"status": "success", "role": role}

        return {"status": "error", "message": "Incorrect password"}
    except Exception as e:
        print("Database error:", e)
        return {"status": "error", "message": "Database error"}


def get_all_products():
    try:
        con = connect_db()
        cursor = con.cursor()
        cursor.execute("SELECT * FROM products")
        records = cursor.fetchall()
        cursor.close()
        con.close()
        return records
    except Exception:
        return []


def get_user_by_username(uname):
    try:
        con = connect_db()
        cursor = con.cursor()
        cursor.execute("SELECT username, password, phoneno, role FROM users WHERE username = ?", (uname,))
        user = cursor.fetchone()
        cursor.close()
        con.close()
        return user
    except Exception as e:
        print("Database error:", e)
        return None


def reset_password(username, phone, new_password):
    """Verifies identity via phone number and resets user password securely."""
    try:
        if not new_password or len(new_password) < 4:
            return "Password must be at least 4 characters long"

        con = connect_db()
        cursor = con.cursor()
        cursor.execute("SELECT phoneno FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        
        if not row or str(row[0]) != str(phone).strip():
            con.close()
            return "Username or phone number incorrect"

        hashed_pwd = ph.hash(new_password)
        cursor.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_pwd, username))
        con.commit()
        con.close()
        return "Password reset successfully"
    except Exception as e:
        return f"Database error: {str(e)}"


def register_user(username, password, phone, role="staff"):
    try:
        con = connect_db()
        cursor = con.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            con.close()
            return "Username already exists"

        hashed_password = ph.hash(password)
        cursor.execute(
            "INSERT INTO users (username, password, phoneno, role) VALUES (?, ?, ?, ?)",
            (username, hashed_password, phone, role)
        )
        con.commit()
        con.close()
        return "User registered successfully"
    except Exception as e:
        return f"Database error: {str(e)}"


def get_all_stockmanage():
    try:
        con = connect_db()
        con.row_factory = sqlite3.Row
        cursor = con.cursor()
        cursor.execute("SELECT * FROM vendor")
        vendors = cursor.fetchall()
        result = [dict(row) for row in vendors]
        cursor.close()
        con.close()
        return result
    except Exception as e:
        print(f"Error in get_all_stockmanage: {e}")
        return []


def _validate_product_fields(data):
    if not str(data.get('pname', '')).strip():
        return "Product name is required"

    for field in ('qty', 'minqty', 'price'):
        try:
            value = int(data[field])
        except (KeyError, ValueError, TypeError):
            return f"'{field}' must be a whole number"
        if value < 0:
            return f"'{field}' cannot be negative"
        data[field] = value

    return None


def generate_qr_code(pid, barcode_value):
    try:
        import qrcode
        qr_dir = os.path.join(BASE_DIR, "static", "qrcodes")
        os.makedirs(qr_dir, exist_ok=True)
        img = qrcode.make(barcode_value)
        img.save(os.path.join(qr_dir, f"{pid}.png"))
        return True
    except Exception as e:
        print(f"Error generating QR code for pid={pid}: {e}")
        return False


def add_product(data):
    error = _validate_product_fields(data)
    if error:
        return f"Error: {error}"
    try:
        con = connect_db()
        cursor = con.cursor()
        cursor.execute(
            """
            INSERT INTO products (pname, category, size, qty, minqty, price, barcode)
            VALUES (?, ?, ?, ?, ?, ?, NULL)
            """,
            (data['pname'], data['category'], data['size'], data['qty'],
             data['minqty'], data['price'])
        )
        pid = cursor.lastrowid
        barcode_value = f"SKU-{pid:05d}"
        cursor.execute("UPDATE products SET barcode = ? WHERE pid = ?", (barcode_value, pid))
        con.commit()
        con.close()

        generate_qr_code(pid, barcode_value)
        return "Product added successfully"
    except sqlite3.IntegrityError:
        return "Error: A product with this name already exists"
    except Exception as e:
        return f"Error: {e}"


def delete_product_by_name(pname):
    """Deletes product, removes static QR label image, and cleans up linked vendor records."""
    try:
        con = connect_db()
        cursor = con.cursor()
        cursor.execute("SELECT pid FROM products WHERE pname = ?", (pname,))
        row = cursor.fetchone()
        
        if not row:
            con.close()
            return "Product not found"
            
        pid = row[0]

        # 1. Delete associated static QR file
        qr_path = Path(BASE_DIR) / "static" / "qrcodes" / f"{pid}.png"
        if qr_path.exists():
            try:
                qr_path.unlink()
            except OSError as e:
                print(f"Error removing QR file {qr_path}: {e}")

        # 2. Clean up associated vendor records
        cursor.execute("DELETE FROM vendor WHERE pid = ? OR pname = ?", (pid, pname))

        # 3. Delete product row
        cursor.execute("DELETE FROM products WHERE pid = ?", (pid,))
        con.commit()
        con.close()
        return "Product deleted successfully"
    except Exception as e:
        return f"Error: {e}"


def get_product_by_barcode(barcode):
    try:
        con = connect_db()
        con.row_factory = sqlite3.Row
        cursor = con.cursor()
        cursor.execute("SELECT * FROM products WHERE barcode = ?", (barcode,))
        row = cursor.fetchone()
        con.close()
        return dict(row) if row else None
    except Exception as e:
        print(f"Error in get_product_by_barcode: {e}")
        return None


def update_product(pname, field, new_value):
    """Updates product details and automatically logs quantity reductions to sales history."""
    try:
        if field not in ("qty", "price", "size"):
            return "Invalid field"

        con = connect_db()
        cursor = con.cursor()

        try:
            new_value = int(new_value)
        except (ValueError, TypeError):
            con.close()
            return f"'{field}' must be a whole number"

        if new_value < 0:
            con.close()
            return f"'{field}' cannot be negative"

        if field == "qty":
            cursor.execute("SELECT pid, qty, minqty FROM products WHERE pname = ?", (pname,))
            result = cursor.fetchone()
            if not result:
                con.close()
                return "Product not found"

            pid, current_qty, minqty = result[0], result[1], result[2]

            # Calculate units sold if new quantity is lower than current stock
            qty_sold = current_qty - new_value

            cursor.execute("UPDATE products SET qty = ? WHERE pname = ?", (new_value, pname))
            con.commit()
            con.close()

            # Record sale transaction permanently
            if qty_sold > 0:
                record_sale(pid, pname, qty_sold=qty_sold, qty_remaining=new_value)

            if new_value < minqty:
                con_v = connect_db()
                cur_v = con_v.cursor()
                cur_v.execute("SELECT email FROM vendor WHERE pname = ? ORDER BY vendorid LIMIT 1", (pname,))
                vendor = cur_v.fetchone()
                vendor_email = vendor[0] if vendor and vendor[0] else None
                con_v.close()
                return {
                    "status": "warning",
                    "message": f"Quantity ({new_value}) is below minimum ({minqty})",
                    "vendor_email": vendor_email,
                    "pname": pname
                }

            return "Product updated successfully"

        # Update non-quantity fields (price, size)
        query = f"UPDATE products SET {field} = ? WHERE pname = ?"
        cursor.execute(query, (new_value, pname))
        con.commit()
        con.close()
        return "Product updated successfully"
    except Exception as e:
        return f"Error: {e}"
    

def update_product_quantity(barcode_data, delta):
    con = connect_db()
    cursor = con.cursor()
    cursor.execute("SELECT pid, pname, qty FROM products WHERE barcode = ?", (barcode_data,))
    row = cursor.fetchone()
    if row is None:
        con.close()
        return "Product not found"
    
    pid, pname, current_qty = row
    new_qty = current_qty + delta
    if new_qty < 0:
        con.close()
        return "Error: Quantity cannot drop below 0"
    
    cursor.execute("UPDATE products SET qty = ? WHERE barcode = ?", (new_qty, barcode_data))
    con.commit()
    con.close()

    # Record sale if delta is negative (e.g. quantity decreased via barcode scanner)
    if delta < 0:
        record_sale(pid, pname, qty_sold=abs(delta), qty_remaining=new_qty)

    return f"Product quantity updated to {new_qty}"


def update_qty_one(pname):
    """Quick Sale handler (-1 button): Decrements stock by 1 and logs sale."""
    con = connect_db()
    cursor = con.cursor()
    cursor.execute("SELECT pid, qty FROM products WHERE pname = ?", (pname,))
    row = cursor.fetchone()
    if row is None:
        con.close()
        return "Product not found"

    pid, current_qty = row
    if current_qty <= 0:
        con.close()
        return "Out of stock"

    new_qty = current_qty - 1
    cursor.execute("UPDATE products SET qty = ? WHERE pname = ?", (new_qty, pname))
    con.commit()
    con.close()

    # Log sale transaction
    record_sale(pid, pname, qty_sold=1, qty_remaining=new_qty)
    return f"User bought {pname}"


def fix_stock_schema():
    """Checks if the stock table matches required columns, recreating it if mismatched."""
    try:
        con = connect_db()
        cursor = con.cursor()
        
        cursor.execute("PRAGMA table_info(stock)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Rebuild table if missing or if legacy/incompatible columns exist
        if not columns or 'qty_sold' not in columns:
            cursor.execute("DROP TABLE IF EXISTS stock")
            cursor.execute("""
                CREATE TABLE stock (
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
    except Exception as e:
        print(f"[DB SCHEMA ERROR] {e}")

# Run schema check when db_utils is loaded
fix_stock_schema()


def record_sale(pid, pname, qty_sold, qty_remaining):
    """Inserts a verified sale into SQLite stock table."""
    if qty_sold <= 0:
        return
    try:
        con = connect_db()
        cursor = con.cursor()
        cursor.execute(
            """
            INSERT INTO stock (pid, pname, qty_sold, qty_remaining, sale_date)
            VALUES (?, ?, ?, ?, ?)
            """,
            (pid, pname, qty_sold, qty_remaining, datetime.datetime.now().isoformat(timespec='seconds'))
        )
        con.commit()
        con.close()
        print(f"[SALE LOGGED] {pname}: Sold {qty_sold}, Remaining {qty_remaining}")
    except Exception as e:
        print(f"[RECORD SALE ERROR] Could not log sale for {pname}: {e}")


def get_inventory_stats():
    """Retrieves live metrics from inventory.db."""
    total_products = 0
    total_value = 0
    low_stock_count = 0
    total_units_sold = 0

    try:
        fix_stock_schema()  # Ensure table exists and is valid
        con = connect_db()
        cursor = con.cursor()

        cursor.execute("SELECT COUNT(*), COALESCE(SUM(qty * price), 0) FROM products")
        row = cursor.fetchone()
        if row:
            total_products = row[0] or 0
            total_value = row[1] or 0

        cursor.execute("SELECT COUNT(*) FROM products WHERE qty <= minqty")
        row = cursor.fetchone()
        if row:
            low_stock_count = row[0] or 0

        cursor.execute("SELECT COALESCE(SUM(qty_sold), 0) FROM stock")
        row = cursor.fetchone()
        if row:
            total_units_sold = row[0] or 0

        con.close()
    except Exception as e:
        print(f"[STATS ERROR] {e}")

    return {
        "total_products": total_products,
        "total_value": total_value,
        "low_stock_count": low_stock_count,
        "total_units_sold": total_units_sold,
    }


def get_sales_history():
    """Fetches all logged sales ordered by latest transaction."""
    try:
        fix_stock_schema()
        con = connect_db()
        con.row_factory = sqlite3.Row
        cursor = con.cursor()
        cursor.execute("SELECT * FROM stock ORDER BY saleid DESC")
        rows = cursor.fetchall()
        con.close()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"[SALES HISTORY ERROR] {e}")
        return []


def add_vendor(data):
    try:
        con = connect_db()
        cursor = con.cursor()
        cursor.execute(
            """
            INSERT INTO vendor (pid, pname, vendorid, vendorname, contactno, email, address)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (data['pid'], data['pname'], data['vendorid'], data['vendorname'],
             data['contactno'], data['email'], data['address'])
        )
        con.commit()
        con.close()
        return "Vendor added successfully"
    except sqlite3.IntegrityError:
        return "Error: Vendor ID already exists"
    except Exception as e:
        return f"Error: {e}"


def delete_vendor_by_id(vendorid):
    try:
        con = connect_db()
        cursor = con.cursor()
        cursor.execute("SELECT * FROM vendor WHERE vendorid = ?", (vendorid,))
        if not cursor.fetchone():
            con.close()
            return "Error: Vendor not found"
        cursor.execute("DELETE FROM vendor WHERE vendorid = ?", (vendorid,))
        con.commit()
        con.close()
        return "Vendor deleted successfully"
    except Exception as e:
        return f"Error: {e}"


def update_vendor(data):
    try:
        con = connect_db()
        cursor = con.cursor()
        cursor.execute("SELECT * FROM vendor WHERE vendorid = ?", (data['vendorid'],))
        if not cursor.fetchone():
            con.close()
            return "Error: Vendor not found"
        cursor.execute(
            """
            UPDATE vendor
            SET pid = ?, pname = ?, vendorname = ?, contactno = ?, email = ?, address = ?
            WHERE vendorid = ?
            """,
            (data['pid'], data['pname'], data['vendorname'], data['contactno'],
             data['email'], data['address'], data['vendorid'])
        )
        con.commit()
        con.close()
        return "Vendor updated successfully"
    except sqlite3.IntegrityError:
        return "Error: Product ID conflict"
    except Exception as e:
        return f"Error: {e}"