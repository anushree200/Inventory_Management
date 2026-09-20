import os,io
import secrets
import sqlite3
import datetime
from functools import wraps
from pathlib import Path
import csv

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, session, flash, send_file, jsonify, Response
from flask_wtf import CSRFProtect
from flask_mail import Mail, Message

try:
    from flask_mail import Mail, Message
except ImportError:
    Mail = None
    Message = None

from db_utils import (
    login_user, register_user, get_all_products,
    get_user_by_username, get_all_stockmanage,
    add_product, delete_product_by_name, update_product,
    update_product_quantity, update_qty_one, add_vendor,
    delete_vendor_by_id, update_vendor, get_sales_history,
    get_inventory_stats, get_product_by_barcode, reset_password
)

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
LOG_PATH = BASE_DIR / "log.txt"


def log_event(message):
    with LOG_PATH.open("a", encoding="utf-8") as logfile:
        logfile.write(f"{message} at time = {datetime.datetime.now().strftime('%H:%M:%S')}\n")


app = Flask(__name__)

_secret_key = os.getenv("FLASK_SECRET_KEY")
if not _secret_key:
    _secret_key = secrets.token_hex(32)
    print("WARNING: FLASK_SECRET_KEY not set — using temporary ephemeral key.")
app.secret_key = _secret_key

csrf = CSRFProtect(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'your_real_email@gmail.com')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'xxxx xxxx xxxx xxxx') # Google App Password
app.config['MAIL_DEFAULT_SENDER'] = ('Inventory System', app.config['MAIL_USERNAME'])

mail = Mail(app)

def send_restock_alert(vendor_email, pname, qty, minqty):
    """Sends an automated low-stock alert email via Flask-Mail."""
    if not vendor_email:
        print(f"[MAIL WARNING] No vendor email provided for {pname}")
        return False

    try:
        msg = Message(
            subject=f"URGENT: Restock Required for {pname}",
            recipients=[vendor_email],
            body=f"Hello,\n\nThe product '{pname}' has dropped below safety stock.\n\nCurrent Stock: {qty}\nMinimum Required: {minqty}\n\nPlease arrange a shipment at your earliest convenience.\n\nAutomated Inventory System"
        )
        mail.send(msg)
        print(f"[MAIL SUCCESS] Restock alert sent to {vendor_email}")
        return True
    except Exception as e:
        print(f"[MAIL ERROR] Failed to send email: {e}")
        return False

    
def owner_required(f):
    """Decorator to restrict sensitive routes to owner accounts."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect('/')
        if session.get('role') != 'owner':
            flash("Access denied: Owner privileges required.", "error")
            return redirect('/products')
        return f(*args, **kwargs)
    return decorated_function


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        res = login_user(uname, pwd)
        if res.get("status") == "success":
            session['user'] = uname
            session['role'] = res.get("role", "staff")
            log_event(f"user logged in under username = {uname} (role: {session['role']})")
            return redirect('/products')
        else:
            log_event(f"failed login attempt for username = {uname}")
            flash(res.get("message", "Login failed"))
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        phone = request.form['phoneno']
        result = register_user(uname, pwd, phone, role="staff")

        if result == "User registered successfully":
            log_event(f"user signed up under username = {uname}")
            flash(result, "success")
            return redirect('/')
        else:
            flash(result, "error")
            return render_template('signup.html')
    return render_template('signup.html')


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        uname = request.form['username']
        phone = request.form['phoneno']
        new_password = request.form['new_password']
        
        result = reset_password(uname, phone, new_password)
        if result == "Password reset successfully":
            log_event(f"password reset completed for username = {uname}")
            flash("Password updated successfully. Please login with your new password.", "success")
            return redirect('/')
        else:
            log_event(f"failed password reset attempt for username = {uname}")
            flash(result, "error")
    return render_template('forgot_password.html')


@app.route('/products')
def products():
    products = get_all_products()
    stats = get_inventory_stats()
    return render_template('products.html', products=products, stats=stats)

@app.route('/stock')
def stock():
    if 'user' not in session:
        return redirect('/')
    vendors = get_all_stockmanage()
    return render_template('stock.html', vendors=vendors)


@app.route('/stock-history')
@owner_required
def stockhis():
    try:
        with LOG_PATH.open("r", encoding="utf-8") as logfile:
            logs = logfile.readlines()
    except FileNotFoundError:
        logs = ["Log file not found."]
    return render_template("stock_history.html", logs=logs)


@app.route('/sales-history')
def sales_history():
    sales = get_sales_history()
    return render_template('sales_history.html', sales=sales)


@app.route('/log.txt')
@owner_required
def serve_log():
    if not LOG_PATH.exists():
        return "Log file not found.", 404
    return send_file(LOG_PATH, mimetype='text/plain')


@app.route('/add-vendor', methods=['GET', 'POST'])
@owner_required
def addvendor():
    if request.method == 'POST':
        data = {
            'pid': request.form['pid'],
            'pname': request.form['pname'],
            'vendorid': request.form['vendorid'],
            'vendorname': request.form['vendorname'],
            'contactno': request.form['contactno'],
            'email': request.form['email'],
            'address': request.form['address']
        }
        result = add_vendor(data)
        log_event(f"user {session['user']} added vendor {data['vendorname']}")
        flash(result)
        return redirect('/stock')
    products = get_all_products()
    return render_template('addvendor.html', products=products)


@app.route('/del-vendor', methods=['GET', 'POST'])
@owner_required
def delvendor():
    if request.method == 'POST':
        vendorid = request.form['vendorid']
        result = delete_vendor_by_id(vendorid)
        log_event(f"user {session['user']} deleted vendor ID {vendorid}")
        flash(result)
        return redirect('/stock')
    vendors = get_all_stockmanage()
    return render_template('delvendor.html', vendors=vendors)


@app.route('/modify-vendor', methods=['GET', 'POST'])
@owner_required
def modvendor():
    if request.method == 'POST':
        data = {
            'vendorid': request.form['vendorid'],
            'pid': request.form['pid'],
            'pname': request.form['pname'],
            'vendorname': request.form['vendorname'],
            'contactno': request.form['contactno'],
            'email': request.form['email'],
            'address': request.form['address']
        }
        result = update_vendor(data)
        log_event(f"user {session['user']} updated vendor ID {data['vendorid']}")
        flash(result)
        return redirect('/stock')
    vendors = get_all_stockmanage()
    products = get_all_products()
    return render_template('modvendor.html', vendors=vendors, products=products)


@app.route('/logout')
def logout():
    uname = session.pop('user', None)
    session.pop('role', None)
    log_event(f"user with username:{uname} logged out")
    return redirect('/')


@app.route('/decrease', methods=['POST'])
def decrease():
    if 'user' not in session:
        return redirect('/')
    pname = request.form['pname']
    log_event(f"user {session['user']} recorded sale for {pname}")
    result = update_qty_one(pname)

    # Check if stock dropped below minqty after Quick Sale
    try:
        conn = sqlite3.connect(str(BASE_DIR / 'inventory.db'))
        cursor = conn.cursor()
        cursor.execute('SELECT qty, minqty FROM products WHERE pname = ?', (pname,))
        prod = cursor.fetchone()
        
        if prod:
            qty, minqty = prod[0], prod[1]
            if qty <= minqty:
                cursor.execute('SELECT email FROM vendor WHERE pname = ? ORDER BY vendorid LIMIT 1', (pname,))
                vendor = cursor.fetchone()
                if vendor and vendor[0]:
                    send_restock_alert(vendor[0], pname, qty, minqty)
        conn.close()
    except Exception as e:
        print(f"[QUICK SALE MAIL ERROR] {e}")

    flash(result)
    return redirect('/products')


@app.route('/barcode', methods=['GET', 'POST'])
def barcode():
    if 'user' not in session:
        return redirect('/')

    if request.method == 'POST':
        code = request.form.get('barcode', '').strip()
        delta_raw = request.form.get('delta', '')

        if not code:
            flash("No barcode received.")
            return redirect('/barcode')

        try:
            delta = int(delta_raw)
        except ValueError:
            flash("Adjustment amount must be a whole number.")
            return redirect('/barcode')

        result = update_product_quantity(code, delta)
        flash(result)
        return redirect('/products')

    return render_template('barcode.html')


@app.route('/api/product-lookup')
def product_lookup():
    if 'user' not in session:
        return jsonify({'error': 'Login required'}), 401

    code = request.args.get('barcode', '').strip()
    if not code:
        return jsonify({'error': 'No barcode provided'}), 400

    product = get_product_by_barcode(code)
    if not product:
        return jsonify({'error': 'No product matches this code'}), 404

    return jsonify({
        'pname': product['pname'],
        'qty': product['qty'],
        'minqty': product['minqty'],
    })


@app.route('/modify-inventory', methods=['GET', 'POST'])
def modify():
    if 'user' not in session:
        return redirect('/')

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            data = {
                'pname': request.form['pname'],
                'category': request.form['category'],
                'size': request.form['size'],
                'qty': request.form['qty'],
                'minqty': request.form['minqty'],
                'price': request.form['price'],
                'barcode': request.form.get('barcode', '')
            }
            result = add_product(data)
            log_event(f"user {session['user']} added product : {data['pname']}")
            flash(result)

        elif action == 'delete':
            if session.get('role') != 'owner':
                flash("Access denied: Only owners can delete products.", "error")
                return redirect('/products')
            pname = request.form['pname']
            result = delete_product_by_name(pname)
            log_event(f"product {pname} deleted by {session['user']}")
            flash(result)

        elif action == 'update':
            pname = request.form['pname']
            field = request.form['update_field']
            new_value = request.form['new_value']
            result = update_product(pname, field, new_value)
            log_event(f"product {pname} field {field} updated to {new_value} by {session['user']}")

            # Handle Low-Stock Warning & Trigger Automated Email
            if isinstance(result, dict) and result.get('status') == 'warning':
                vendor_email = result.get('vendor_email')
                
                if vendor_email:
                    send_restock_alert(vendor_email, pname, new_value, "configured minimum")

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify(result)
                flash(result['message'], 'warning')
                return render_template('modify_inventory.html', alert_data=result, products=get_all_products())

            flash(result, 'success' if result == "Product updated successfully" else 'error')
        return redirect('/products')

    products = get_all_products()
    return render_template('modify_inventory.html', products=products)


@app.route('/send-vendor-email', methods=['POST'])
def send_vendor_email():
    if 'user' not in session:
        return jsonify({'message': 'Login required'}), 401

    data = request.get_json() or {}
    pname = data.get('pname')
    vendor_email = data.get('email')

    if not vendor_email:
        return jsonify({'message': 'No vendor email provided'}), 400

    if mail is None or Message is None:
        return jsonify({'message': 'Email service is not configured. Set MAIL_USERNAME and MAIL_PASSWORD in .env.'}), 500

    conn = sqlite3.connect(str(BASE_DIR / 'inventory.db'))
    cursor = conn.cursor()
    cursor.execute('SELECT qty, minqty FROM products WHERE pname = ?', (pname,))
    product = cursor.fetchone()
    conn.close()

    if not product:
        return jsonify({'message': 'Product not found'}), 404

    qty, minqty = product
    subject = f'Low Stock Alert for Product: {pname}'
    body = f"""Dear Vendor,

The stock for product '{pname}' is running low.
Current Quantity: {qty}
Minimum Quantity: {minqty}

Please arrange to restock at your earliest convenience.

Regards,
Inventory Management Team"""

    try:
        msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[vendor_email])
        msg.body = body
        mail.send(msg)
        return jsonify({'message': 'Email sent successfully'})
    except Exception as exc:
        return jsonify({'message': f'Failed to send email: {str(exc)}'}), 500

@app.route('/export-sales-csv')
def export_sales_csv():
    sales = get_sales_history()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write CSV Header
    writer.writerow(['Sale ID', 'Product ID', 'Product Name', 'Quantity Sold', 'Remaining Stock', 'Sale Date / Time'])
    
    # Write Data Rows
    for s in sales:
        writer.writerow([
            s.get('saleid', ''),
            s.get('pid', ''),
            s.get('pname', ''),
            s.get('qty_sold', ''),
            s.get('qty_remaining', ''),
            s.get('sale_date', '')
        ])
    
    # Return response as downloadable file
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=sales_history_report.csv"}
    )

if __name__ == '__main__':
    app.run(debug=os.getenv("FLASK_DEBUG", "False").lower() in ("1", "true", "yes"))