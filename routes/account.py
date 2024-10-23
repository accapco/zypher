from flask import Blueprint, request, session, render_template, redirect, url_for, jsonify

from models.account import Account
from models.location import Area, Zipcode, LocationName

account_bp = Blueprint('account', __name__)

@account_bp.before_request
def verify_loggedin():
    if request.path not in ('/account/login', '/account/register') and 'loggedin' not in session:
        return redirect(url_for('home'))
    
@account_bp.route('/', methods=['GET'])
def index():
    return render_template("account/base.html")

@account_bp.route('/details', methods=['GET', 'POST'])
def details():
    response = Account.get(session['user_id'])
    if response['status'] == "error":
        return jsonify(response), response['status_code']  # Fix: added return

    user = response['user']
    regions, areas, zipcodes = Account.get_regions_areas_zipcodes(user)

    # Fetch region name
    region_name = None
    if user['region_id']:
        region_query = LocationName.get_region_name(user['region_id'])
        region_name = region_query['RegionName'] if region_query else None
        print("region names: ", region_name)

    # Fetch area name
    area_name = None
    if user['area_id']:
        area_query = LocationName.get_area_name(user['area_id'])
        area_name = area_query['Area'] if area_query else None
        print("area name: ", area_name)

    if request.method == 'GET' and not request.args.get('partial') == "true":
        return render_template("account/details.html", base_html="account/base.html", user=user, 
                               regions=regions, areas=areas, zipcodes=zipcodes,
                               region_name=region_name, area_name=area_name)

    if request.method == 'POST':
        response = Account.update(request.form)
        html = render_template("account/details.html", base_html="ajax.html", user=user, 
                               regions=regions, areas=areas, zipcodes=zipcodes, 
                               region_name=region_name, area_name=area_name)

        response['html'] = html
        return jsonify(response), response['status_code']

    # Handle other cases
    html = render_template("account/details.html", base_html="ajax.html", user=user, 
                           regions=regions, areas=areas, zipcodes=zipcodes, 
                           region_name=region_name, area_name=area_name)
    return jsonify({'html': html}), 200
    
@account_bp.route('/orders', methods=['GET'])
def orders():
    user_id = session.get('user_id')

    # Validate user_id parameter
    if not user_id:
        return jsonify({'message': 'You are not logged in.'}), 400

    # Fetch orders from the model
    order_data = Account.get_orders(user_id)
    if order_data['status'] == 'error':
        return jsonify({'message': order_data['message']}), order_data['status_code']

    # Extract orders from the result, ensuring it's a list
    orders = list(order_data['orders'])  # Convert tuple to list if necessary

    # Render template based on request type
    if request.args.get('partial') != "true":
        return render_template("account/orders.html", base_html="account/base.html", orders=orders)

    html = render_template('account/orders.html', base_html="ajax.html", orders=orders)
    return jsonify({'html': html}), 200

@account_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({'message': 'You are not logged in.'}), 400

    order_data = Account.get_order(user_id, order_id)

    if order_data['status'] == 'error':
        return jsonify({'message': order_data['message']}), order_data['status_code']

    order = order_data['order']

    if request.args.get('partial') != "true":
        return render_template("account/order_item.html", base_html="account/base.html", order=order)

    html = render_template('account/order_item.html', base_html="ajax.html", order=order)
    return jsonify({'html': html}), 200

@account_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        response = Account.register(request.form)

        if response['status'] == "success":
            session['loggedin'] = True
            session['user_id'] = response['user']['user_id']

        response['redirect'] = url_for('home')
        return jsonify(response), response['status_code']
    
    html = render_template('account/register.html')
    return jsonify({'html': html}), 200

@account_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        response = Account.login(request.form)

        if response['status'] == "success":
            session['loggedin'] = True
            session['user_id'] = response['user']['user_id']
        
        response['redirect'] = url_for('home')
        return jsonify(response), response['status_code']

    html = render_template('account/login.html')
    return jsonify({'html': html}), 200


@account_bp.route('/areas/<int:region_id>')
def get_areas(region_id):
    print("RegionID: ", region_id)
    areas = Area.get_by_region(region_id)
    area_list = [(area['AreaID'], area['Area']) for area in areas]  # Use dictionary keys
    return jsonify(area_list)

@account_bp.route('/zipcodes/<int:area_id>')
def get_zipcodes(area_id):
    zipcodes = Zipcode.get_by_area(area_id)
    zipcode_list = [(zipcode['ZipCodeID'], zipcode['ZipCode']) for zipcode in zipcodes]  # Use dictionary keys
    return jsonify(zipcode_list)

@account_bp.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('user_id', None)
    return redirect(url_for('home'))