from flask import render_template, request, url_for, Blueprint, jsonify

from models.orders import Orders

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/', methods=['GET'])
def getall():
    orders_data = Orders.getall()
    orders = orders_data.get('orders')
    html = render_template("orders/getall.html", orders=orders)
    return jsonify({"html": html, "message": orders_data.get('message')}), orders_data['status_code']


@orders_bp.route('<int:order_id>/confirm_order', methods=['POST'])
def confirm_order(order_id):
    result = Orders.confirm_order(order_id)

    if result['status'] == "success":
        print(f"Order {order_id} successfully confirmed.")
    else:
        print(f"Order {order_id} confirmation failed: {result['message']}")

    # Send only the success or failure message
    return jsonify({"message": result['message'], "status": result['status']}), result['status_code']



