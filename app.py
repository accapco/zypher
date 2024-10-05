from flask import Flask, render_template, url_for, redirect
from flask_mysqldb import MySQL
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
    return render_template('home.html')

@app.route('/catalog')
def catalog():
    response = categories.getall()
    category_tree = response.json['category_tree']
    response = products.getall()
    products_list = response.json['products']
    return render_template('catalog.html', category_tree=category_tree, products_list=products_list)

#@app.route('/viewproduct')
#def viewproduct():
#    return render_template('viewproduct.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(debug=True)