from flask import Flask, render_template,request, redirect, url_for, session, Blueprint, flash
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
            SELECT cart_items.cart_item_id, cart_items.cart_id, cart_items.price, 
                   cart_items.quantity, products.product_name, products.image_url
            FROM cart_items
            INNER JOIN cart ON cart_items.cart_id = cart.cart_id
            INNER JOIN products ON cart_items.product_id = products.product_id
            WHERE cart.user_id = %s
        ''', (user_id,))
        cart_items = cursor.fetchall()
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
        cursor.execute('''
            SELECT cart_items.cart_item_id, cart_items.cart_id, cart_items.price, 
                   cart_items.quantity, products.product_name, products.image_url
            FROM cart_items
            INNER JOIN cart ON cart_items.cart_id = cart.cart_id
            INNER JOIN products ON cart_items.product_id = products.product_id
            WHERE cart.user_id = %s
        ''', (user_id,))
        cart_items = cursor.fetchall()
        
        return render_template('cart.html', cart_items=cart_items)  
    return redirect(url_for('login'))


@app.route('/viewproduct', methods=['GET', 'POST'])
def addtocart():
    if 'loggedin' in session:
       if 'loggedin' in session and 'user_id' in session:
        user_id = request.args.get('user_id')
        if request.method == 'POST':
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
                flash('Product added to cart successfully!', 'success')

            except Exception as e:
                flash(f'Error adding product to cart: {str(e)}', 'danger')

            return redirect('/catalog')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Products WHERE is_active = TRUE')
        products = cursor.fetchall()

        return render_template('catalog.html', catalog=products)

    return redirect(url_for('login'))


@app.route('/archiveproduct', methods=['GET', 'POST'])
def getarchiveproduct():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
            SELECT p.*, c.category_name 
            FROM products p 
            JOIN categories c ON p.category_id = c.category_id 
            WHERE p.is_active = FALSE
        ''')
        prdcts = cursor.fetchall()
        return render_template("archiveproduct.html", getproducts=prdcts)
    return redirect(url_for('login'))

@app.route('/viewproduct/<int:product_id>', methods=['GET'])
def viewproduct(product_id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM products WHERE product_id = %s AND is_active = TRUE', (product_id,))
        product = cursor.fetchone()

        if product:
            cursor.execute('SELECT image_url FROM product_images WHERE product_id = %s', (product_id,))
            images = cursor.fetchall()
            product['images'] = images
            return render_template('products/viewproduct.html', product=product)
        else:
            flash('Product not found or inactive.', 'danger')
            return redirect(url_for('getproducts'))
    return redirect(url_for('login'))