from flask import render_template, url_for, redirect, session, request, jsonify
import json

from models.products import Products
from models.categories import Categories
from models.cart import Cart
from models.users import Users
from models.orders import Orders

from app import app

@app.route('/')
def index():    
    return redirect(url_for('.home'))

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/catalog')
def catalog():
    # get filters
    filters = {
        'category_tree': Categories.getall(as_tree=True).get('category_tree'),
        'colors': Products.colors().get('colors'),
        'sizes': Products.sizes().get('sizes')
    }
    return render_template('catalog.html', filters=filters)

@app.route('/catalog/<int:product_id>')
def catalog_get(product_id):
    product = Products.get(product_id).get('product')
    return render_template('catalog_item.html', product=product)

@app.route('/prepare_checkout', methods=['POST'])
def prepare_checkout():
    try:
        selected_items = request.form.get('selected_items')
        selected_items = json.loads(selected_items)
        session['checkout_items'] = selected_items
        return jsonify({'redirect': url_for('.checkout')}), 200
    except Exception as e:
        return jsonify({'redirect': url_for('.checkout')}), 500

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    user = Users.get(session['user_id']).get('user')
    items = session.get('checkout_items')
    if request.method == 'POST':
        response = Orders.add(session['user_id'], request.form, items)
        if response['status'] == "success":
            response['redirect'] = url_for('.order_summary', order_id=response['order_id'])
        else:
            response['redirect'] = url_for('.home')
        return jsonify(response), response['status_code']
    
    total = sum(float(i['price']) * int(i['quantity']) for i in items)
    return render_template("checkout.html", user=user, selected_items=items, total=total)

@app.route('/order_summary/<int:order_id>', methods=['GET'])
def order_summary(order_id):
    order = Orders.get(order_id)
    return render_template("order_summary.html", order_summary=order)

@app.route('/admin')
def admin():
    return render_template('admin.html')

# Inject cart count into all templates
@app.context_processor
def inject_cart_info():
    cart_items = []
    cart_count = 0
    if 'loggedin' in session:
        response = Cart.getall(session['user_id'])
        cart_items = response['cart']
        cart_count = response['count']
    return dict(cart_count=cart_count, cart_items=cart_items)