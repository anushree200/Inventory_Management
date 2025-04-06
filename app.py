from flask import Flask, render_template, request, redirect, url_for, session, flash
from db_utils import login_user, get_all_products

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
            return redirect('/dashboard')
        else:
            flash(result)
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    products = get_all_products()
    return render_template('dashboard.html', products=products)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
