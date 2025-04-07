from flask import Flask, render_template, request, redirect, url_for, session, flash
from db_utils import (
    login_user, register_user, get_all_products,
    get_user_by_username, get_all_stockmanage,
    add_product, delete_product_by_name, update_product
)
import datetime
app = Flask(__name__)
app.secret_key = "secret123"
f = open("log.txt",'a')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        result = login_user(uname, pwd)
        if result == "Success":
            session['user'] = uname
            f.write(f"user logged in under username = {uname} at time = {datetime.datetime.now().strftime('%H:%M:%S')}")
            return redirect('/products')
        else:
            f.write(f"user tried logging in under username = {uname} at time = {datetime.datetime.now().strftime('%H:%M:%S')}, but failed")
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
            f.write(f"user signedup under username = {uname} at time ={datetime.datetime.now().strftime('%H:%M:%S')}")
            flash(result)
            return redirect('/')
        else:
            flash(result)
            return render_template('signup.html')
    return render_template('signup.html')
@app.route('/stock-history')
def stockhis():
    return render_template("stock_history.html")

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        uname = request.form['username']
        phone = request.form['phoneno']
        user = get_user_by_username(uname)

        if user and str(user[2]) == phone:
            f.write(f"forgot password by username = {uname} at time = {datetime.datetime.now().strftime('%H:%M:%S')}")
            flash(f"Your password is: {user[1]}")
            return render_template('forgot_password_result.html')
        else:
            f.write(f"an user tried to get their password at time = {datetime.datetime.now().strftime('%H:%M:%S')}")
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
    session.pop('user', None)
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
            f.write(f"user added a product with name : {data['pname']} of size : {data['size']} at time = {datetime.datetime.now().strftime('%H:%M:%S')}")
            flash(result)

        elif action == 'delete':
            pname = request.form['pname']
            result = delete_product_by_name(pname)
            f.write(f"a product with name : {pname} was deleted at time = {datetime.datetime.now().strftime('%H:%M:%S')}")
            flash(result)

        elif action == 'update':
            pname = request.form['pname']
            field = request.form['update_field']
            new_value = request.form['new_value']
            result = update_product(pname, field, new_value)
            f.write(f"a product with name : {pname}'s {field} was updated to {new_value} at time = {datetime.datetime.now().strftime('%H:%M:%S')}")
            flash(result)

        return redirect('/products')

    return render_template('modify_inventory.html')
if __name__ == '__main__':
    app.run(debug=True)
