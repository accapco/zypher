from flask import Flask, render_template, url_for, redirect, session, request
from flask_mysqldb import MySQL
import MySQLdb.cursors
from config import config
import os

app = Flask(__name__)
app.config.from_object('config.Config')

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

mysql = MySQL(app)

import account
import users
import products
import categories
import cart

app.register_blueprint(account.account_bp, url_prefix='/account')
app.register_blueprint(users.users_bp, url_prefix='/users')
app.register_blueprint(products.products_bp, url_prefix='/products')
app.register_blueprint(categories.categories_bp, url_prefix='/categories')


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
    # get categories
    response = categories.getall()
    category_tree = response.json['category_tree']
    # get products and filter

    cart_items = []
    cart_count = 0
    if 'loggedin' in session:
        user_id = session['user_id']
        cart_items, cart_count = get_cart_items(user_id)

    return render_template('catalog.html', 
                           category_tree=category_tree, 
                           cart_items=cart_items, 
                           cart_count=cart_count)


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
    cart_count = 0
    if 'loggedin' in session:
        user_id = session['user_id']
        cart_items, cart_count = get_cart_items(user_id)
    return dict(cart_count=cart_count)


#@app.route('/viewproduct')
#def viewproduct():
#    return render_template('viewproduct.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

if __name__ == '__main__':
    app.run()