from flask import render_template, url_for, redirect, session, request, jsonify
import json

from models.products import Products
from models.categories import Categories
from models.cart import Cart
from models.users import Users
from models.orders import Orders
from models.location import Area, Zipcode, LocationName

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
    
    # Fetch region and area names
    region_name = None
    area_name = None
    
    if user['region_id']:
        region_query = LocationName.get_region_name(user['region_id'])
        region_name = region_query['RegionName'] if region_query else None
    
    if user['area_id']:
        area_query = LocationName.get_area_name(user['area_id'])
        area_name = area_query['Area'] if area_query else None

    if request.method == 'POST':
        response = Orders.add(session['user_id'], request.form, items)
        if response['status'] == "success":
            response['redirect'] = url_for('.checkout_summary', order_id=response['order_id'])
        else:
            response['redirect'] = url_for('.home')
        return jsonify(response), response['status_code']
    
    total = sum(float(i['price']) * int(i['quantity']) for i in items)
    return render_template("checkout.html", user=user, selected_items=items, total=total,
                           region_name=region_name, area_name=area_name)

@app.route('/checkout_summary/<int:order_id>', methods=['GET'])
def checkout_summary(order_id):
    order_data = Orders.get(order_id)
    order = order_data['order']
    return render_template("checkout_summary.html", order=order), order_data['status_code']

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

from babel.dates import format_datetime

@app.template_filter()
def format_time(value, format='medium'):
    if format == 'full':
        format="EEEE, d. MMMM y 'at' h:mm a"
    elif format == 'medium':
        format="MMM d, y h:mm a"
    return format_datetime(value, format)