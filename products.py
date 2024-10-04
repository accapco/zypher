from flask import Flask, render_template,request, redirect, url_for, session, flash, Blueprint, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from app import mysql
from config import config
from werkzeug.utils import secure_filename
import os

products_bp = Blueprint('products', __name__)

@products_bp.before_request
def verify_loggedin():
    if 'loggedin' not in session:
        return redirect(url_for('home'))
    
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@products_bp.route('/', methods=['GET'])
def getall():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT p.*, c.category_name 
        FROM products p 
        JOIN categories c ON p.category_id = c.category_id 
        WHERE p.is_active = TRUE
    ''')
    products = cursor.fetchall()
    products_html = render_template("products/getall.html", products=products)
    return jsonify({"html": products_html, "products": products})

@products_bp.route('/<int:product_id>')
def get(product_id):
    cursor = mysql.connection(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM products WHERE product_id = %s', (product_id,))
    product = cursor.fetchone()
    product_html = render_template("products/get.html", product=product)
    return jsonify({"html": product_html})

@products_bp.route('/add', methods=['GET', 'POST'])
def add():
    msg = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        categoryid = request.form['category_id']
        productname = request.form['product_name']
        description = request.form['description']
        price = request.form['price']
        stockqty = request.form['stock_quantity']
        size = request.form['size']
        color = request.form['color']
        images = request.files.getlist('images')
        if images and allowed_file(images[0].filename):
            first_image = images[0]
            filename = secure_filename(first_image.filename)
            image_path = os.path.join(config.UPLOAD_FOLDER, filename)
            first_image.save(image_path)
            cursor.execute('''INSERT INTO products (category_id, product_name, description, price, stock_quantity, size, color, image_url) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
                            (categoryid, productname, description, price, stockqty, size, color, filename))
            product_id = cursor.lastrowid  
            for image in images:
                if allowed_file(image.filename):
                    filename = secure_filename(image.filename)
                    image_path = os.path.join(config.UPLOAD_FOLDER, filename)
                    image.save(image_path)
                    cursor.execute('INSERT INTO product_images (product_id, image_url) VALUES (%s, %s)', (product_id, filename))
            mysql.connection.commit()
            msg = 'Product and images added successfully!'
        else:
            msg = 'Please upload at least one valid image file.', 'danger'
    cursor.execute('SELECT category_id, category_name FROM categories WHERE is_archived = FALSE')
    categories = cursor.fetchall()
    add_product_html = render_template('products/add.html', categories=categories)
    return jsonify({'html': add_product_html, 'message': msg})

@products_bp.route('/<int:product_id>/edit', methods=['GET', 'POST'])
def edit(product_id):
    msg = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM products WHERE product_id = %s', (product_id,))
    product = cursor.fetchone()
    cursor.execute('SELECT category_id, category_name FROM categories WHERE is_archived = FALSE')
    categories = cursor.fetchall()
    if request.method == 'POST':
        try:
            categoryid = request.form['category_id']
            productname = request.form['product_name']
            description = request.form['description']
            price = request.form['price']
            stockqty = request.form['stock_quantity']
            size = request.form['size']
            color = request.form['color']
            image_file = request.files.get('image') 
            if image_file:
                image_filename = secure_filename(image_file.filename)
                image_file.save(os.path.join('uploads', image_filename))  # Save the file
                cursor.execute('UPDATE products SET category_id = %s, product_name = %s, description = %s, price = %s, stock_quantity = %s, size = %s, color = %s, image = %s WHERE product_id = %s', 
                                (categoryid, productname, description, price, stockqty, size, color, image_filename, product_id))
            else:
                cursor.execute('UPDATE products SET category_id = %s, product_name = %s, description = %s, price = %s, stock_quantity = %s, size = %s, color = %s WHERE product_id = %s', 
                                (categoryid, productname, description, price, stockqty, size, color, product_id))
            mysql.connection.commit()
            msg = 'Successfully updated product details.'
        except:
            msg = 'Problem occured while making changes to product details.'
    edit_product_html = render_template("products/edit.html", product=product, categories=categories) 
    return jsonify({'html': edit_product_html, 'message': msg})

@products_bp.route('/archiveproduct', methods=['POST'])
def archiveproduct():
    product_id = request.form.get('product_id')       
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM products WHERE product_id = %s', (product_id,))
    products = cursor.fetchone()
    
    if products:     
        cursor.execute('''
            UPDATE products
            SET is_active = FALSE
            WHERE product_id = %s
        ''', (product_id,))
        mysql.connection.commit()
    return redirect(url_for('getproducts'))

@products_bp.route('/restoreproduct', methods=['POST'])
def restoreproduct():
    product_id = request.form.get('product_id')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM products WHERE product_id = %s', (product_id,))
    archived_product = cursor.fetchone()

    if archived_product:
        cursor.execute('''
            UPDATE products
            SET is_active = 1
            WHERE product_id = %s
        ''', (product_id,))
        mysql.connection.commit()
    return redirect(url_for('getproducts'))

@products_bp.route('/archiveproduct', methods=['GET', 'POST'])
def getarchiveproduct():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT p.*, c.category_name 
        FROM products p 
        JOIN categories c ON p.category_id = c.category_id 
        WHERE p.is_active = FALSE
    ''')
    prdcts = cursor.fetchall()
    return render_template("archiveproduct.html", getproducts=prdcts)