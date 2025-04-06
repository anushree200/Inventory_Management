from flask import Flask, render_template, request, redirect, url_for, session, flash
from db_utils import login_user, register_user, get_all_products, get_user_by_username
import requests
app = Flask(__name__)
app.secret_key = "secret123"

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        result = login_user(uname, pwd)
        if result == "Success":
            session['user'] = uname
            return redirect('/products')
        else:
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
            flash(result)
            return redirect('/')
        else:
            flash(result)
            return render_template('signup.html')
    return render_template('signup.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        uname = request.form['username']
        phone = request.form['phoneno']
        user = get_user_by_username(uname)
        
        if user and str(user[2]) == phone:  # assuming user[2] is phone and user[1] is password
            flash(f"Your password is: {user[1]}")
        else:
            flash("Username or phone number incorrect")
            
    return render_template('forgot_password.html')


@app.route('/products')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    products = get_all_products()
    return render_template('products.html', products=products)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
