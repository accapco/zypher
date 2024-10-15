from flask import Flask, render_template, url_for, redirect, session, request, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import json
import os

app = Flask(__name__)
app.config.from_object('config.Config')

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

mysql = MySQL(app)

import account, users, products, categories, orders, cart

app.register_blueprint(account.account_bp, url_prefix='/account')
app.register_blueprint(users.users_bp, url_prefix='/users')
app.register_blueprint(products.products_bp, url_prefix='/products')
app.register_blueprint(categories.categories_bp, url_prefix='/categories')
app.register_blueprint(orders.orders_bp, url_prefix='/orders')
app.register_blueprint(cart.cart_bp, url_prefix='/cart')

@app.route('/')
def index():    
    return redirect(url_for('.home'))

@app.route('/home')
def home():
    cart_items = []
    cart_count = 0
    if 'loggedin' in session:
        user_id = session['user_id']
        cart_items, cart_count = get_cart_items(user_id)

    return render_template('home.html',
                           cart_items=cart_items, 
                           cart_count=cart_count)

@app.route('/catalog')
def catalog():
    # get filters
    filters = {
        'category_tree': categories.getall().json['category_tree'],
        'colors': products.get_colors().json['colors'],
        'sizes': products.get_sizes().json['sizes']
    }
    # cart item counter
    cart_items = []
    cart_count = 0
    if 'loggedin' in session:
        user_id = session['user_id']
        cart_items, cart_count = get_cart_items(user_id)
    return render_template('catalog.html', 
                           filters=filters, 
                           cart_items=cart_items, 
                           cart_count=cart_count)

@app.route('/catalog/<int:product_id>')
def catalog_get(product_id):
    # cart item counter
    cart_items = []
    cart_count = 0
    if 'loggedin' in session:
        user_id = session['user_id']
        cart_items, cart_count = get_cart_items(user_id)
    product = products.get(product_id).json['product']
    return render_template('catalog_item.html', 
                           product=product,
                           cart_items=cart_items, 
                           cart_count=cart_count)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'GET':
        selected_items = session.get('checkout_items')
        total = sum(float(item['price']) * int(item['quantity']) for item in selected_items)
        user_id = session['user_id']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT email, first_name, last_name, address, city FROM tbl_users WHERE user_id = %s', (user_id,))
        user_info = cursor.fetchone()
        cursor.close()

        return render_template("checkout.html", user_info=user_info, selected_items=selected_items, total=total)

    if request.method == 'POST':
        contact_info = request.form['contact']
        shipping_address = f"{request.form['f_name']} {request.form['l_name']}, {request.form['address']}, {request.form['city']}, {request.form['postal']}, {request.form['region']}"
        payment_method = request.form['payment']
        billing_address = shipping_address if request.form['billing'] == 'same' else f"{request.form['f_name']} {request.form['l_name']}, {request.form['address']}, {request.form['city']}, {request.form['postal']}, {request.form['region']}"

        selected_items = session.get('checkout_items')
        user_id = session['user_id']

        total = sum(float(item['price']) * int(item['quantity']) for item in selected_items)
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO Orders (user_id, order_date, status, total_amount, shipping_address) VALUES (%s, NOW(), %s, %s, %s)', 
                       (user_id, payment_method, total, shipping_address))
        mysql.connection.commit()

        order_id = cursor.lastrowid

        for item in selected_items:
            product_id = item['product_id']  # This should match the key used when formatting items
            quantity = item['quantity']
            price = item['price']

            order_count = cursor.execute('SELECT COUNT(*) FROM Order_Summary WHERE product_id = %s', (product_id,))
            order_count += 1
            order_number = f"ZYPHER{product_id}{str(order_count).zfill(3)}"

            cursor.execute('INSERT INTO Order_Summary (order_id, order_number, contact_info, shipping_address, payment_method, billing_address, product_id, quantity, price) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                           (order_id, order_number, contact_info, shipping_address, payment_method, billing_address, product_id, quantity, price))

        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('order_summary', order_id=order_id))

@app.route('/order_summary/<int:order_id>', methods=['GET'])
def order_summary(order_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM Order_Summary WHERE order_id = %s', (order_id,))
    order_summary = cursor.fetchall()
    cursor.close()
    
    return render_template("order_summary.html", order_summary=order_summary)

@app.route('/admin')
def admin():
    return render_template('admin.html')

def get_cart_items(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT cart_items.cart_item_id, cart_items.cart_id, cart_items.price, 
               cart_items.quantity, products.product_name, products.image_url
        FROM cart_items
        INNER JOIN cart ON cart_items.cart_id = cart.cart_id
        INNER JOIN products ON cart_items.product_id = products.product_id
        WHERE cart.user_id = %s
    ''', (user_id,))
    cart_items = cursor.fetchall()
    return cart_items, len(cart_items)

@app.context_processor
def inject_cart_info():
    """Inject cart count into all templates."""
    cart_items = []
    cart_count = 0
    if 'loggedin' in session:
        user_id = session['user_id']
        cart_items, cart_count = get_cart_items(user_id)
    return dict(cart_count=cart_count, cart_items=cart_items)

if __name__ == '__main__':
    app.run()




 
@app.route('/prepare_checkout', methods=['POST'])
def prepare_checkout():
    try:
        selected_items = request.form.get('selected_items')
        selected_items = json.loads(selected_items)
        session['checkout_items'] = selected_items
        print("Selected items: ", selected_items)
        return jsonify({'redirect': url_for('checkout')}), 200
    except Exception as e:
        return jsonify({'redirect': url_for('checkout')}), 500

"""@app.route('/checkout', methods=['GET'])
def checkout():
    if request.method == 'GET':
        selected_items = session.get('checkout_items')
        total = sum(float(item['price']) * int(item['quantity']) for item in selected_items)
        # Fetch user details from the session
        user_id = session['user_id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT email, first_name, last_name, address, city FROM tbl_users WHERE user_id = %s', (user_id,))
        user_info = cursor.fetchone()
        cursor.close()
        return render_template("checkout.html", user_info=user_info, selected_items=selected_items, total=total)"""
