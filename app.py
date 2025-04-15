from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, Response
from db_utils import (
    login_user, register_user, get_all_products,
    get_user_by_username, get_all_stockmanage,
    add_product, delete_product_by_name, update_product,
    update_product_quantity,update_qty_one, add_vendor, delete_vendor_by_id, update_vendor
)
import datetime,cv2
app = Flask(__name__)
app.secret_key = "secret123"
f = open("C:\\Users\\aanuu\\Downloads\\inventoryupdated\\Inventory_Management\\log.txt", 'a')


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        result = login_user(uname, pwd)
        if result == "Success":
            session['user'] = uname
            f.write(f"user logged in under username = {uname} at time = {datetime.datetime.now().strftime('%H:%M:%S')}\n")
            f.flush()
            return redirect('/products')
        else:
            f.write(f"user tried logging in under username = {uname} at time = {datetime.datetime.now().strftime('%H:%M:%S')}, but failed\n")
            f.flush()
            flash(result)
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        phone = request.form['phoneno']
        result = register_user(uname, pwd, phone)
        
        if result == "User registered successfully":
            f.write(f"user signedup under username = {uname} at time ={datetime.datetime.now().strftime('%H:%M:%S')}\n")
            f.flush()
            flash(result)
            return redirect('/')
        else:
            flash(result)
            return render_template('signup.html')
    return render_template('signup.html')

@app.route('/stock-history')
def stockhis():
    try:
        with open("log.txt", "r") as logfile:
            logs = logfile.readlines()
    except FileNotFoundError:
        logs = ["Log file not found."]
    return render_template("stock_history.html", logs=logs)

@app.route('/log.txt')
def serve_log():
    return send_file("C:/Users/aanuu/Downloads/inventoryupdated/Inventory_Management/log.txt")

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        uname = request.form['username']
        phone = request.form['phoneno']
        user = get_user_by_username(uname)

        if user and str(user[2]) == phone:
            f.write(f"forgot password by username = {uname} at time = {datetime.datetime.now().strftime('%H:%M:%S')}\n")
            f.flush()
            return render_template('forgot_password_result.html')
        else:
            f.write(f"an user tried to get their password at time = {datetime.datetime.now().strftime('%H:%M:%S')}\n")
            f.flush()
            flash("Username or phone number incorrect")
    return render_template('forgot_password.html')

@app.route('/products')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    products = get_all_products()
    return render_template('products.html', products=products)

@app.route('/stock')
def stock():
    vendors = get_all_stockmanage()
    return render_template('stock.html',vendors = vendors)

@app.route('/add-vendor', methods=['GET', 'POST'])
def addvendor():
    if 'user' not in session:
        return redirect('/')
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
        f.write(f"user {session['user']} added vendor {data['vendorname']} (ID: {data['vendorid']}) at time = {datetime.datetime.now().strftime('%H:%M:%S')}\n")
        f.flush()
        flash(result)
        return redirect('/stock')
    f.write(f"adding a vendor at time = {datetime.datetime.now().strftime('%H:%M:%S')}\n")
    f.flush()
    return render_template('addvendor.html')

@app.route('/del-vendor', methods=['GET', 'POST'])
def delvendor():
    if 'user' not in session:
        return redirect('/')
    if request.method == 'POST':
        vendorid = request.form['vendorid']
        result = delete_vendor_by_id(vendorid)
        f.write(f"user {session['user']} deleted vendor ID {vendorid} at time = {datetime.datetime.now().strftime('%H:%M:%S')}\n")
        f.flush()
        flash(result)
        return redirect('/stock')
    f.write(f"deleting a vendor at time = {datetime.datetime.now().strftime('%H:%M:%S')}\n")
    f.flush()
    return render_template('delvendor.html')

@app.route('/modify-vendor', methods=['GET', 'POST'])
def modvendor():
    if 'user' not in session:
        return redirect('/')
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
        f.write(f"user {session['user']} updated vendor ID {data['vendorid']} at time = {datetime.datetime.now().strftime('%H:%M:%S')}\n")
        f.flush()
        flash(result)
        return redirect('/stock')
    f.write(f"modifying a vendor details at time = {datetime.datetime.now().strftime('%H:%M:%S')}\n")
    f.flush()
    return render_template('modvendor.html')

@app.route('/logout')
def logout():
    uname = session.pop('user', None)
    f.write(f"user with username:{uname} logged out at time = {datetime.datetime.now().strftime('%H:%M:%S')}\n")
    f.flush()
    return redirect('/')

@app.route('/decrease',methods=['POST'])
def decrease():
    pname = request.form['pname']
    f.write(f"user bought a {pname} at time = {datetime.datetime.now().strftime('%H:%M:%S')}\n")
    f.flush()
    result = update_qty_one(pname)
    flash(result)
    return redirect('/products')

@app.route('/barcode', methods=['GET', 'POST'])
def barcode():
    mode = request.args.get('mode', 'adjust')

    if request.method == 'POST':
        camera = cv2.VideoCapture(0)
        detector = cv2.QRCodeDetector()
        data = ''

        for _ in range(30):
            ret, frame = camera.read()
            if not ret:
                continue

            data, bbox, _ = detector.detectAndDecode(frame)

            print("Decoded data:", data)

            if data:
                break

        camera.release()

        if data:
            if mode == 'scan-only':
                session['scanned_barcode'] = data
                return redirect('/modify-inventory')
            else:
                delta = int(request.form['delta'])
                result = update_product_quantity(data, delta)
                flash(result)
                return redirect('/products')

        flash("QR code not detected.")
        return redirect('/barcode')

    return render_template('barcode.html', mode=mode)

@app.route('/modify-inventory', methods=['GET', 'POST'])
def modify():
    if 'user' not in session:
        return redirect('/')

    if request.method == 'POST':
        action = request.form['action']

        if action == 'add':
            data = {
                'pname': request.form['pname'],
                'category': request.form['category'],
                'size': request.form['size'],
                'qty': request.form['qty'],
                'minqty': request.form['minqty'],
                'price': request.form['price'],
                'barcode': request.form['barcode']
            }
            result = add_product(data)
            f.write(f"user added a product with name : {data['pname']} of quantity : {data['qty']} at time = {datetime.datetime.now().strftime('%H:%M:%S')}\n")
            f.flush()
            flash(result)

        elif action == 'delete':
            pname = request.form['pname']
            result = delete_product_by_name(pname)
            f.write(f"a product with name : {pname} was deleted at time = {datetime.datetime.now().strftime('%H:%M:%S')}\n")
            f.flush()
            flash(result)

        elif action == 'update':
            pname = request.form['pname']
            field = request.form['update_field']
            new_value = request.form['new_value']
            result = update_product(pname, field, new_value)
            f.write(f"a product with name : {pname}'s {field} was updated to {new_value} at time = {datetime.datetime.now().strftime('%H:%M:%S')}\n")
            f.flush()
            flash(result)

        return redirect('/products')

    return render_template('modify_inventory.html')
if __name__ == '__main__':
    app.run(debug=True)
