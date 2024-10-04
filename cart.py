from flask import Flask, render_template,request, redirect, url_for, session, Blueprint
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from app import app, mysql

cart_bp = Blueprint('cart', __name__)

@app.route('/cart')
def cart():
    if 'loggedin' in session:
        user_id = session['user_id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
            SELECT cart_items.cart_item_id, cart_items.cart_id, cart_items.price, cart_items.quantity, products.product_name
            FROM cart_items
            INNER JOIN cart ON cart_items.cart_id = cart.cart_id
            INNER JOIN products ON cart_items.product_id = products.product_id
            WHERE cart.user_id = %s
        ''', (user_id,))
        print(user_id)
        cart_items = cursor.fetchall()
        print(cart_items)  
        return render_template('cart.html', cart_items=cart_items)  
    
    return render_template('login.html')  



@app.route('/removecart', methods=['GET', 'POST'])
def removecart():
    if 'loggedin' in session:
        removecart_id = request.args.get('cart_item_id')  
        user_id = session['user_id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE FROM cart_items WHERE cart_item_id = %s', (removecart_id,)) 
        mysql.connection.commit()
        print(removecart_id)
        cursor.execute('''
            SELECT cart_items.cart_item_id, cart_items.cart_id, cart_items.price, cart_items.quantity, products.product_name
            FROM cart_items
            INNER JOIN cart ON cart_items.cart_id = cart.cart_id
            INNER JOIN products ON cart_items.product_id = products.product_id
            WHERE cart.user_id = %s
        ''', (user_id,))
        cart_items = cursor.fetchall()
        
        return render_template('cart.html', cart_items=cart_items)  
    return redirect(url_for('login'))