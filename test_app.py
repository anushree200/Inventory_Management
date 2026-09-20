import os
import sqlite3
import pytest
import db_utils
from app import app


@pytest.fixture
def db(tmp_path, monkeypatch):
    db_path = tmp_path / "test_inventory.db"
    monkeypatch.setattr(db_utils, "DB_PATH", str(db_path))

    con = sqlite3.connect(str(db_path))
    cur = con.cursor()
    cur.execute('''CREATE TABLE users (username TEXT PRIMARY KEY, password TEXT NOT NULL, phoneno INTEGER, role TEXT NOT NULL DEFAULT 'staff')''')
    cur.execute('''CREATE TABLE products (
        pid INTEGER PRIMARY KEY AUTOINCREMENT, pname TEXT NOT NULL UNIQUE, category TEXT,
        size INTEGER, qty INTEGER NOT NULL, minqty INTEGER NOT NULL,
        price INTEGER NOT NULL, barcode TEXT UNIQUE)''')
    cur.execute('''CREATE TABLE vendor (
        pid INTEGER, pname TEXT NOT NULL, vendorid INTEGER PRIMARY KEY,
        vendorname TEXT, contactno INTEGER, email TEXT, address TEXT)''')
    cur.execute('''CREATE TABLE stock (
        saleid INTEGER PRIMARY KEY AUTOINCREMENT, pid INTEGER, pname TEXT NOT NULL,
        qty_sold INTEGER NOT NULL, qty_remaining INTEGER NOT NULL, sale_date TEXT NOT NULL)''')
    con.commit()
    con.close()
    return db_path


@pytest.fixture
def client(db):
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client


# --- Password Reset Flow ---

def test_password_reset_success(db):
    db_utils.register_user("alice", "oldpass123", "9876543210")
    res = db_utils.reset_password("alice", "9876543210", "newpass123")
    assert res == "Password reset successfully"
    
    login_res = db_utils.login_user("alice", "newpass123")
    assert login_res["status"] == "success"


def test_password_reset_fails_on_mismatched_phone(db):
    db_utils.register_user("alice", "oldpass123", "9876543210")
    res = db_utils.reset_password("alice", "0000000000", "newpass123")
    assert "incorrect" in res.lower()


# --- Vendor CRUD Operations ---

def test_vendor_crud_lifecycle(db):
    # Add Vendor
    res_add = db_utils.add_vendor({
        "pid": 1, "pname": "Widget", "vendorid": 101,
        "vendorname": "Acme Corp", "contactno": 12345,
        "email": "acme@example.com", "address": "City"
    })
    assert res_add == "Vendor added successfully"
    assert len(db_utils.get_all_stockmanage()) == 1

    # Update Vendor
    res_upd = db_utils.update_vendor({
        "pid": 1, "pname": "Widget", "vendorid": 101,
        "vendorname": "Acme Updated", "contactno": 54321,
        "email": "updated@example.com", "address": "New City"
    })
    assert res_upd == "Vendor updated successfully"
    vendors = db_utils.get_all_stockmanage()
    assert vendors[0]["vendorname"] == "Acme Updated"

    # Delete Vendor
    res_del = db_utils.delete_vendor_by_id(101)
    assert res_del == "Vendor deleted successfully"
    assert len(db_utils.get_all_stockmanage()) == 0


# --- Deletion Cleanup (Files & Vendors) ---

def test_product_deletion_cleans_qrcodes_and_vendors(db, tmp_path, monkeypatch):
    monkeypatch.setattr(db_utils, "BASE_DIR", str(tmp_path))
    qr_dir = tmp_path / "static" / "qrcodes"
    qr_dir.mkdir(parents=True)

    db_utils.add_product({
        "pname": "Gadget", "category": "Tech", "size": 1,
        "qty": 10, "minqty": 2, "price": 100, "barcode": "SKU-00001"
    })
    db_utils.add_vendor({
        "pid": 1, "pname": "Gadget", "vendorid": 201,
        "vendorname": "Supplier", "contactno": 111,
        "email": "s@test.com", "address": "Address"
    })

    # Create dummy QR file
    dummy_qr = qr_dir / "1.png"
    dummy_qr.write_text("fake_image_data")
    assert dummy_qr.exists()

    res = db_utils.delete_product_by_name("Gadget")
    assert res == "Product deleted successfully"
    assert not dummy_qr.exists()
    assert len(db_utils.get_all_stockmanage()) == 0


# --- RBAC Route Protection ---

def test_staff_cannot_access_owner_routes(client, db):
    db_utils.register_user("staff_user", "password123", "1234567890", role="staff")
    
    with client.session_transaction() as sess:
        sess['user'] = 'staff_user'
        sess['role'] = 'staff'

    # Attempt to delete vendor
    response = client.post('/del-vendor', data={'vendorid': 101}, follow_redirects=True)
    assert b"Access denied" in response.data

    # Attempt to view log file
    response_log = client.get('/log.txt', follow_redirects=True)
    assert response_log.status_code == 302 or b"Access denied" in response_log.data


def test_owner_can_access_restricted_routes(client, db):
    db_utils.register_user("owner_user", "password123", "9999999999", role="owner")

    with client.session_transaction() as sess:
        sess['user'] = 'owner_user'
        sess['role'] = 'owner'

    response = client.get('/add-vendor')
    assert response.status_code == 200


def test_sales_history_nav_is_on_products_page_not_vendor_management(client, db):
    with client.session_transaction() as sess:
        sess['user'] = 'owner_user'
        sess['role'] = 'owner'

    products_response = client.get('/products')
    stock_response = client.get('/stock')

    assert products_response.status_code == 200
    assert b'href="/sales-history"' in products_response.data
    assert b'href="/sales-history"' not in stock_response.data