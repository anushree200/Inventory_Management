from flask import Flask, render_template, request, redirect, url_for, session, flash
from db_utils import login_user, register_user, get_all_products, get_user_by_username
import requests
app = Flask(__name__)
app.secret_key = "secret123"
FAST2SMS_API_KEY = "vdEL0NGzCy8DxcbHKVQ9l3go4ZIwT1jiA5uFSnpO6Btr2aPWkUvg8S27IhZXKVkWsM1yGdP3w5OqDNuY"
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
        phone = request.form['phone']
        result = register_user(uname, pwd, phone)
        flash(result)
        return redirect('/')
    return render_template('signup.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        uname = request.form['username']
        phone = request.form['phone']
        user = get_user_by_username(uname)
        if user and str(user[2]) == phone:
            # Send password via Fast2SMS
            msg = f"Your password is: {user[1]}"
            payload = {
                "sender_id": "FSTSMS",
                "message": msg,
                "language": "english",
                "route": "p",
                "numbers": str(user[2])
            }
            headers = {
                'authorization': FAST2SMS_API_KEY,
                'Content-Type': "application/x-www-form-urlencoded",
                'Cache-Control': "no-cache"
            }

            try:
                response = requests.post("https://www.fast2sms.com/dev/bulk", data=payload, headers=headers)
                if response.status_code == 200:
                    flash("Password has been sent to your phone.")
                else:
                    flash("Failed to send SMS. Try again later.")
            except Exception as e:
                flash(f"SMS Error: {str(e)}")
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
