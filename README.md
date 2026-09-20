# Inventory Management System

A Flask-based inventory management system for a small shop or warehouse:
add products, track stock in real time, get automatic low-stock alerts to
vendors, and scan printed labels with any device's camera to sell or
restock without typing.

## Features

- **Authentication** — Argon2-hashed passwords, with automatic migration of
  any legacy plaintext passwords to hashed ones on next login.
- **Dashboard** — total products, total inventory value, low-stock count,
  and units sold at a glance on the main products page.
- **Product management** — add, update, delete products. Product names are
  unique, enforced at the database level.
- **Auto-generated labels** — every product gets a barcode value and a
  printable QR code the moment it's created (`SKU-00001`, etc.) — no
  manual entry, no typos.
- **Barcode scanning** — every product gets a barcode value and a
  printable QR code the moment it's created (`SKU-00001`, etc.). Scan the
  printed label with a physical USB/Bluetooth barcode scanner (or just
  type the code by hand — the input field doesn't care which) to sell or
  restock a product, with a confirmation step showing what was scanned
  before anything is committed.
- **Vendor management** — CRUD for vendor records tied to products.
- **Low-stock alerts** — when a product's quantity drops below its
  configured minimum, the system flags it and can email the associated
  vendor directly from the UI.
- **Sales history** — every sale is logged to a dedicated table, separate
  from the general activity log.
- **Audit log** — every significant action (login, logout, product/vendor
  changes) is timestamped and logged.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# then edit .env and set at least FLASK_SECRET_KEY:
python -c "import secrets; print(secrets.token_hex(32))"

python setup_db.py          # creates inventory.db with a demo user (anu / anu123)
python app.py
```

Run the tests with:
```bash
pytest
```

## Using the scanner

1. Add a product from **Modify Inventory** — a barcode/QR label is
   generated automatically.
2. Open it from the products table (the small QR thumbnail in the "Label"
   column) and print it, or just note the code printed next to it.
3. Click the scanner icon in the top bar. The page opens with a text
   field already focused — scan the label with a connected barcode
   scanner (or type the code by hand), press Enter, and confirm the
   quantity change (negative to sell, positive to restock).

**No physical scanner needed to try this out.** USB/Bluetooth barcode
scanners are "HID keyboard emulator" devices — to the browser, a scan is
indistinguishable from someone typing the code and pressing Enter. So the
scan page works identically whether the code came from a real scanner or
was typed by hand; there's nothing scanner-specific to install, configure,
or grant permission to.

## Architecture notes

- **Scanning requires no camera, no HTTPS, and no browser permissions** —
  it's a plain focused text input listening for Enter (see
  `static/js/barcode.js`). An earlier version of this used
  `cv2.VideoCapture(0)` server-side, which opened the webcam attached to
  whatever machine ran the Flask process rather than the actual user's
  device — that only worked as a local demo. A later version used the
  browser's camera directly, which works but needs HTTPS and camera
  permission on every device. A physical HID scanner (or manual typing)
  needs neither.
- **CSRF protection** is enabled via Flask-WTF on every POST form.
- **SQLite**, chosen for simplicity/portability of a student/demo project.
  For a "production-grade" story, the natural next step is Postgres plus
  a migration tool (Alembic) instead of the current idempotent
  `CREATE TABLE IF NOT EXISTS` script.
- **No rate limiting** on login/signup — `Flask-Limiter` would be a quick
  addition if this needs to withstand brute-force attempts.

## Tech stack

Python, Flask, SQLite, Argon2 (password hashing), `qrcode` (label
generation), Flask-Mail, Flask-WTF (CSRF).