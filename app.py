from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from db_utils import (
    login_user, register_user, get_all_products,
    get_user_by_username, get_all_stockmanage,
    add_product, delete_product_by_name, update_product
)
import datetime
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
    stock = get_all_stockmanage()
    return render_template('stock.html',stocks = stock)

@app.route('/logout')
def logout():
    uname = session.pop('user', None)
    f.write(f"user with username:{uname} logged out at time = {datetime.datetime.now().strftime('%H:%M:%S')}\n")
    f.flush()
    return redirect('/')
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
