from flask import render_template, request, url_for, Blueprint, jsonify

from models.orders import Orders

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/', methods=['GET'])
def getall():
    orders_data = Orders.getall()
    orders = orders_data.get('orders')
    html = render_template("orders/getall.html", orders=orders)
    return jsonify({"html": html, "message": orders_data.get('message')}), orders_data['status_code']

@orders_bp.route('/<int:order_id>/schedule_shipment', methods=['GET', 'POST'])
def schedule_shipment(order_id):
    if request.method == 'POST':
        response = Orders.schedule_shipment(order_id)
        response['redirect'] = url_for('.getall')
        return jsonify(response), response['status_code']
    order_data = Orders.get(order_id)
    html = render_template("orders/schedule_shipment.html", order=order_data['order'])
    return jsonify({"html": html, "message": order_data.get('message')}), order_data['status_code']