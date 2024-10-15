from flask import Blueprint, request, session, render_template, redirect, url_for, jsonify
import MySQLdb.cursors
import re

from app import mysql

account_bp = Blueprint('account', __name__)

@account_bp.before_request
def verify_loggedin():
    if request.path not in ('/account/login', '/account/register') and 'loggedin' not in session:
        return redirect(url_for('home'))
    
@account_bp.route('/', methods=['GET'])
def account():
    return render_template("account/account.html")

@account_bp.route('/details', methods=['GET'])
def details():
    user = _get_user()
    return render_template("account/details.html", user=user)

@account_bp.route('/orders', methods=['GET'])
def orders():
    orders = _get_orders()
    return render_template("account/orders.html", orders=orders)

def _get_user():
    user_id = session['user_id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_users WHERE user_id = %s', (user_id,))
    user = cursor.fetchone()
    return user

def _update_user(userName, email, first_name, last_name, phone, address, city, state, zipcode, country, userId):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'UPDATE tbl_users SET username=%s, email=%s, first_name=%s, last_name=%s, phone=%s, address=%s, city=%s, state=%s, zipcode=%s, country=%s WHERE user_id=%s', 
            (userName, email, first_name, last_name, phone, address, city, state, zipcode, country, userId)
        )
        mysql.connection.commit()
        return "Account details have been saved."
    except Exception as e:
        return "Error updating user: {}".format(e)

@account_bp.route('/api/details', methods=['GET', 'POST'])
def api_details():
    msg = ''    
    user = _get_user()    
    if request.method == 'POST' and 'username' in request.form and 'email' in request.form:
        userName = request.form['username']   
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']         
        phone = request.form['phone']
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        zipcode = request.form['zipcode']
        country = request.form['country']
        userId = request.form['userid'] 
        if not re.match(r'[A-Za-z0-9]+', userName):
            msg = 'Username must contain only characters and numbers.'
        else:
            msg = _update_user(userName, email, first_name, last_name, phone, address, city, state, zipcode, country, userId)
    elif request.method == 'POST':
        msg = 'Required fields are empty'
    account_details_html = render_template("account/inner_details.html", user=user)  
    return jsonify({'html': account_details_html, 'message': msg})

# dito pull ng data paedit nalang
def _get_orders():
    orders = [
        {'product_name': "Supreme T-Shirt", 'image_url': "supreme-tshirt.png", 'size': "M", 'color': "White", 'quantity': 1, 'status': "shipped", 'price': 2500, 'paymentmethod': "COD"},
        {'product_name': "Supreme T-Shirt", 'image_url': "supreme-tshirt.png", 'size': "M", 'color': "White", 'quantity': 1, 'status': "received", 'price': 2500, 'paymentmethod': "Bank Transfer"},
        {'product_name': "Supreme T-Shirt", 'image_url': "supreme-tshirt.png", 'size': "M", 'color': "White", 'quantity': 1, 'status': "to ship", 'price': 2500, 'paymentmethod': "GCash"},
        {'product_name': "Supreme T-Shirt", 'image_url': "supreme-tshirt.png", 'size': "M", 'color': "White", 'quantity': 1, 'status': "reviewed", 'price': 2500, 'paymentmethod': "GCash"},
        {'product_name': "Supreme T-Shirt", 'image_url': "supreme-tshirt.png", 'size': "M", 'color': "White", 'quantity': 1, 'status': "reviewed", 'price': 2500, 'paymentmethod': "Bank Transfer"}
    ]
    return orders

@account_bp.route('/api/orders', methods=['GET', 'POST'])
def api_orders():
    orders = _get_orders()
    html = render_template('account/inner_orders.html', orders=orders)
    return jsonify({'html': html})

@account_bp.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_users WHERE email = %s AND password_hash = %s', (email, password,))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['username'] = user['username']
            session['email'] = user['email']
            session['user_id'] = user['user_id']
            return redirect(url_for('home')) 
        else:
            message = 'Please enter correct email/password!'
    login_html = render_template('account/login.html', message=message)
    return jsonify({'html': login_html})

@account_bp.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    session.pop('email', None)
    session.pop('user_id', None)
    return redirect(url_for('home'))

@account_bp.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        userName = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_users WHERE email = %s', (email,))
        account = cursor.fetchone()
        if account:
            message = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address!'
        elif not userName or not password or not email:
            message = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO tbl_users (username, email, password_hash) VALUES (%s, %s, %s)', (userName, email, password))
            mysql.connection.commit()
            message = 'You have successfully registered!'
            return redirect(url_for('home'))
    elif request.method == 'POST':
        message = 'Please fill out the form!'
    register_html = render_template('account/register.html', message=message)
    return jsonify({'html': register_html})