"""
Run with: pytest

Uses a fresh temp SQLite DB per test (via monkeypatch on db_utils.DB_PATH),
so tests never touch your real inventory.db.
"""
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import db_utils  # noqa: E402


@pytest.fixture
def db(tmp_path, monkeypatch):
    db_path = tmp_path / "test_inventory.db"
    monkeypatch.setattr(db_utils, "DB_PATH", str(db_path))

    con = sqlite3.connect(str(db_path))
    cur = con.cursor()
    cur.execute('''CREATE TABLE users (username TEXT PRIMARY KEY, password TEXT NOT NULL, phoneno INTEGER)''')
    cur.execute('''CREATE TABLE products (
        pid INTEGER PRIMARY KEY AUTOINCREMENT, pname TEXT NOT NULL, category TEXT,
        size INTEGER, qty INTEGER NOT NULL, minqty INTEGER NOT NULL,
        price INTEGER NOT NULL, barcode TEXT)''')
    cur.execute('''CREATE TABLE vendor (
        pid INTEGER, pname TEXT NOT NULL, vendorid INTEGER PRIMARY KEY,
        vendorname TEXT, contactno INTEGER, email TEXT, address TEXT)''')
    cur.execute('''CREATE TABLE stock (
        saleid INTEGER PRIMARY KEY AUTOINCREMENT, pid INTEGER, pname TEXT NOT NULL,
        qty_sold INTEGER NOT NULL, qty_remaining INTEGER NOT NULL, sale_date TEXT NOT NULL)''')
    con.commit()
    con.close()
    return db_path


# --- Auth ---------------------------------------------------------------

def test_register_and_login_success(db):
    result = db_utils.register_user("alice", "hunter22", "9999999999")
    assert result == "User registered successfully"
    assert db_utils.login_user("alice", "hunter22") == "Success"


def test_login_wrong_password(db):
    db_utils.register_user("alice", "hunter22", "9999999999")
    assert db_utils.login_user("alice", "wrongpass") == "Incorrect password"


def test_login_unknown_user(db):
    assert db_utils.login_user("ghost", "whatever") == "Please check the username"


def test_duplicate_registration_rejected(db):
    db_utils.register_user("alice", "hunter22", "9999999999")
    result = db_utils.register_user("alice", "different", "1111111111")
    assert result == "Username already exists"


def test_legacy_plaintext_password_migrates_on_login(db):
    # Simulate an old-style plaintext row, as if created before hashing existed.
    con = sqlite3.connect(str(db))
    con.execute("INSERT INTO users (username, password, phoneno) VALUES (?, ?, ?)",
                ("legacyuser", "plainpassword", 1234567890))
    con.commit()
    con.close()

    assert db_utils.login_user("legacyuser", "plainpassword") == "Success"

    con = sqlite3.connect(str(db))
    stored = con.execute("SELECT password FROM users WHERE username = ?", ("legacyuser",)).fetchone()[0]
    con.close()
    assert stored.startswith("$argon2")  # upgraded, not stored as plaintext anymore


# --- Product validation ---------------------------------------------------

def test_add_product_success(db):
    result = db_utils.add_product({
        "pname": "Widget", "category": "Tools", "size": 1,
        "qty": 10, "minqty": 2, "price": 500, "barcode": "12345"
    })
    assert result == "Product added successfully"
    assert len(db_utils.get_all_products()) == 1


def test_add_product_rejects_negative_qty(db):
    result = db_utils.add_product({
        "pname": "Widget", "category": "Tools", "size": 1,
        "qty": -5, "minqty": 2, "price": 500, "barcode": "12345"
    })
    assert "cannot be negative" in result
    assert len(db_utils.get_all_products()) == 0


def test_add_product_rejects_non_numeric_qty(db):
    result = db_utils.add_product({
        "pname": "Widget", "category": "Tools", "size": 1,
        "qty": "ten", "minqty": 2, "price": 500, "barcode": "12345"
    })
    assert "whole number" in result


def test_add_product_rejects_empty_name(db):
    result = db_utils.add_product({
        "pname": "  ", "category": "Tools", "size": 1,
        "qty": 5, "minqty": 2, "price": 500, "barcode": "12345"
    })
    assert "name is required" in result


# --- Low-stock warning + sales logging ------------------------------------

def test_update_qty_below_minimum_returns_warning(db):
    db_utils.add_product({
        "pname": "Widget", "category": "Tools", "size": 1,
        "qty": 10, "minqty": 5, "price": 500, "barcode": "12345"
    })
    result = db_utils.update_product("Widget", "qty", 2)
    assert isinstance(result, dict)
    assert result["status"] == "warning"


def test_buying_last_unit_is_rejected_when_out_of_stock(db):
    db_utils.add_product({
        "pname": "Widget", "category": "Tools", "size": 1,
        "qty": 0, "minqty": 1, "price": 500, "barcode": "12345"
    })
    result = db_utils.update_qty_one("Widget")
    assert result == "Out of stock"


def test_buying_a_product_logs_a_sale(db):
    db_utils.add_product({
        "pname": "Widget", "category": "Tools", "size": 1,
        "qty": 3, "minqty": 1, "price": 500, "barcode": "12345"
    })
    db_utils.update_qty_one("Widget")

    sales = db_utils.get_sales_history()
    assert len(sales) == 1
    assert sales[0]["pname"] == "Widget"
    assert sales[0]["qty_sold"] == 1
    assert sales[0]["qty_remaining"] == 2