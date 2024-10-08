from flask import Blueprint, request, session, render_template, redirect, url_for, jsonify
import MySQLdb.cursors
import re

from app import mysql

users_bp = Blueprint('users', __name__)

@users_bp.before_request
def verify_loggedin():
    if 'loggedin' not in session:
        return redirect(url_for('home'))

@users_bp.before_request
def load_cart_items():
    """Load cart items for the session before each request."""
    cart_items = []
    cart_count = 0
    if 'loggedin' in session:
        user_id = session['user_id']
        cart_items, cart_count = get_cart_items(user_id)
    session['cart_items'] = cart_items
    session['cart_count'] = cart_count

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

@users_bp.route('/', methods=['GET', 'POST'])
def getall():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_users')
    users = cursor.fetchall()
    cart_count = session.get('cart_count', 0)  
    users_html = render_template("users/getall.html", users=users, cart_count=cart_count)    
    return jsonify({'html': users_html})

@users_bp.route('/<int:user_id>', methods=['GET', 'POST'])
def get(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_users WHERE user_id = %s', (user_id,))
    user = cursor.fetchone()
    cart_count = session.get('cart_count', 0)  
    user_html = render_template("users/get.html", user=user, cart_count=cart_count)    
    return jsonify({'html': user_html})

@users_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
def edit(user_id):
    msg = ''    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_users WHERE user_id = %s', (user_id,))
    user = cursor.fetchone()
    cart_count = session.get('cart_count', 0)  
    if request.method == 'POST' and 'username' in request.form and 'email' in request.form:
        # Get form data
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

        if not re.match(r'[A-Za-z0-9]+', userName):
            msg = 'Username must contain only characters and numbers!'
        else:
            cursor.execute(
                'UPDATE tbl_users SET username=%s, email=%s, first_name=%s, last_name=%s, phone=%s, address=%s, city=%s, state=%s, zipcode=%s, country=%s WHERE user_id=%s', 
                (userName, email, first_name, last_name, phone, address, city, state, zipcode, country, user_id)
            )
            mysql.connection.commit()
            msg = 'User details have been updated'
    elif request.method == 'POST':
        msg = 'Some required fields are empty'
<<<<<<< HEAD
    
    edit_html = render_template("users/edit.html", user=user, cart_count=cart_count)    
    return jsonify({'html': edit_html, 'message': msg})
=======
    edit_html = render_template("users/edit.html", user=user)    
    return jsonify({'html': edit_html, 'message': msg, 'redirect': url_for('.getall')})
>>>>>>> 327b1b5efe6f01714de6827f40623b13def78788

@users_bp.route('/<int:user_id>/delete', methods=['GET', 'POST'])
def delete(user_id):
    msg = ''
    delete_html = None
    if request.method == 'POST':
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('DELETE FROM tbl_users WHERE user_id = %s', (user_id,))
            mysql.connection.commit()
            msg = 'User deleted successfully'
        except Exception as e:
            msg = 'Error deleting user'
        return jsonify({'message': msg, 'redirect': url_for('.getall')})
    else:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_users WHERE user_id = %s', (user_id,))
        user = cursor.fetchone()
        delete_html = render_template("users/delete.html", user=user)   
<<<<<<< HEAD
        return jsonify({'html': delete_html})
=======
        return jsonify({'html': delete_html, 'redirect': url_for('.getall')})
>>>>>>> 327b1b5efe6f01714de6827f40623b13def78788
