from flask import render_template, request, url_for, Blueprint, jsonify

from models.orders import Orders

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/', methods=['GET'])
def getall():
    orders = Orders.getall().get('orders')
    orders_html = render_template("orders/getall.html", orders=orders)
    return jsonify({"html": orders_html}), 200