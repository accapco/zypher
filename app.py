from flask import Flask
from flask_mysqldb import MySQL
import os

app = Flask(__name__)
app.config.from_object('config.Config')

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

mysql = MySQL(app)

from routes import main, users, products, categories, orders, cart, account

app.register_blueprint(account.account_bp, url_prefix='/account')
app.register_blueprint(users.users_bp, url_prefix='/users')
app.register_blueprint(products.products_bp, url_prefix='/products')
app.register_blueprint(categories.categories_bp, url_prefix='/categories')
app.register_blueprint(orders.orders_bp, url_prefix='/orders')
app.register_blueprint(cart.cart_bp, url_prefix='/cart')

if __name__ == '__main__':
    app.run()