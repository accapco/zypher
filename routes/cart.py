from flask import render_template, request, session, Blueprint, jsonify

from models.cart import Cart

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/')
def index():
    if 'loggedin' in session:
        response = Cart.getall(session['user_id'])
        cart_items = response['cart']
        cart_count = response['count']
    else:
        cart_items, cart_count = [], 0
    return render_template('cart.html', cart_items=cart_items, cart_count=cart_count)

@cart_bp.route('/add', methods=['POST'])
def add():
    if 'loggedin' in session:
        response = Cart.add(session['user_id'], request.form)
        return jsonify(response), response['status']
    else:
        return jsonify({'message': 'You must be logged in first.', 'status': "warning"}), 401

@cart_bp.route('/<int:cart_id>/remove', methods=['POST'])
def remove(cart_id):
    if 'loggedin' in session:
        response = Cart.remove(cart_id)
        return jsonify(response), response['status']
    else:
        return jsonify({'message': "You must be logged in first.", 'status': "warning"})
