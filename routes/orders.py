from flask import  render_template, request, url_for, flash, Blueprint, jsonify
import MySQLdb.cursors
from app import mysql, app
from werkzeug.utils import secure_filename
import os

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/', methods=['GET'])
def getall():
    orders = [
        {'product_name': "Supreme T-Shirt", 'image_url': "supreme-tshirt.png", 'size': "M", 'color': "White", 'quantity': 1, 'order_id': "ZYPHER00001", 'status': "shipped", 'price': 2500, 'paymentmethod': "COD"},
        {'product_name': "Supreme T-Shirt", 'image_url': "supreme-tshirt.png", 'size': "M", 'color': "White", 'quantity': 1, 'order_id': "ZYPHER00002", 'status': "received", 'price': 2500, 'paymentmethod': "Bank Transfer"},
        {'product_name': "Supreme T-Shirt", 'image_url': "supreme-tshirt.png", 'size': "M", 'color': "White", 'quantity': 1, 'order_id': "ZYPHER00003", 'status': "to ship", 'price': 2500, 'paymentmethod': "GCash"},
        {'product_name': "Supreme T-Shirt", 'image_url': "supreme-tshirt.png", 'size': "M", 'color': "White", 'quantity': 1, 'order_id': "ZYPHER00004", 'status': "reviewed", 'price': 2500, 'paymentmethod': "GCash"},
        {'product_name': "Supreme T-Shirt", 'image_url': "supreme-tshirt.png", 'size': "M", 'color': "White", 'quantity': 1, 'order_id': "ZYPHER00005", 'status': "reviewed", 'price': 2500, 'paymentmethod': "Bank Transfer"}
    ]
    orders_html = render_template("orders/getall.html", orders=orders)
    return jsonify({"html": orders_html})