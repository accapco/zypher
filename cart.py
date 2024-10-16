from flask import Flask, render_template,request, redirect, url_for, session, Blueprint, flash, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from app import app, mysql

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/')
def get():
    if 'loggedin' in session:
        cart_items, cart_count = get_cart_items(session['user_id'])
    else:
        cart_items, cart_count = [], 0
    return render_template('cart.html', cart_items=cart_items, cart_count=cart_count)

@cart_bp.route('/add', methods=['POST'])
def add():
    if 'loggedin' in session:
        try:
            product_id = request.form.get('product_id')
            price = request.form.get('price')
            
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT cart_id FROM Cart WHERE user_id = %s', (session['user_id'],))
            cart = cursor.fetchone()

            if not cart:
                cursor.execute('INSERT INTO Cart (user_id) VALUES (%s)', (session['user_id'],))
                mysql.connection.commit()  
                cursor.execute('SELECT LAST_INSERT_ID() AS cart_id')
                cart = cursor.fetchone()

            cart_id = cart['cart_id']

            cursor.execute('SELECT * FROM Cart_Items WHERE product_id = %s AND cart_id = %s', (product_id, cart_id))
            cart_item = cursor.fetchone()

            if cart_item:
                cursor.execute('UPDATE Cart_Items SET quantity = quantity + 1 WHERE product_id = %s AND cart_id = %s', (product_id, cart_id))
            else:
                cursor.execute('INSERT INTO Cart_Items (cart_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)', 
                                (cart_id, product_id, 1, price))
            mysql.connection.commit()
            return jsonify({'message': 'Item added to cart.', 'status': "success"}), 201
        except Exception as e:
            return jsonify({'message': 'Error adding product. [{e}]'.format(e), 'status': "error"}), 500
    else:
        return jsonify({'message': 'You must login first', 'status': "warning"}), 401

@cart_bp.route('/<int:cart_id>/remove', methods=['POST'])
def remove(cart_id):
    if 'loggedin' in session:
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('DELETE FROM cart_items WHERE cart_item_id = %s', (cart_id,)) 
            mysql.connection.commit()
            return jsonify({'message': "Item has been removed from the cart.", 'status': "info"})
        except Exception as e:
            return jsonify({'message': "Error removing item from the cart. [{}]".format(e), 'status': "error"})
    else:
        return jsonify({'message': "You must be logged in first.", 'status': "warning"})
    

def get_cart_items(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT cart_items.cart_item_id, cart_items.cart_id, cart_items.price, 
               cart_items.quantity, products.product_name, products.image_url,
               products.color, products.size
        FROM cart_items
        INNER JOIN cart ON cart_items.cart_id = cart.cart_id
        INNER JOIN products ON cart_items.product_id = products.product_id
        WHERE cart.user_id = %s
    ''', (user_id,))
    cart_items = cursor.fetchall()
    return cart_items, len(cart_items)

