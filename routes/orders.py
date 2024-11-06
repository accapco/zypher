from flask import render_template, request, url_for, Blueprint, jsonify

from models.orders import Orders

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/', methods=['GET'])
def getall():
    orders_data = Orders.getall()
    orders = orders_data.get('orders')
    html = render_template("orders/getall.html", orders=orders)
    return jsonify({"html": html, "message": orders_data.get('message')}), orders_data['status_code']


@orders_bp.route('/<int:order_id>/confirm_order', methods=['GET', 'POST'])
def confirm_order(order_id):
    if request.method == 'POST':
        result = Orders.confirm_order(order_id)
        result['redirect'] = url_for('.getall')

        if result['status'] == "success":
            print(f"Order {order_id} successfully confirmed.")
        else:
            print(f"Order {order_id} confirmation failed: {result['message']}")

        # Send only the success or failure message
        return jsonify(result), result['status_code']
    # GET
    order_data = Orders.get(order_id)
    html = render_template("orders/confirm_order.html", order=order_data['order'])
    return jsonify({"html": html, "message": order_data.get('message')}), order_data['status_code']



