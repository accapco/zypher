from flask import Blueprint, request, session, render_template, redirect, url_for, jsonify

from models.account import Account

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
        jsonify(response), response['status_code']
    user = response['user']

    if request.method == 'GET' and not request.args.get('partial') == "true":
        return render_template("account/details.html", base_html="account/base.html", user=user)

    if request.method == 'POST':
        response = Account.update(request.form)
        html = render_template("account/details.html", base_html="ajax.html", user=user) 
        response['html'] = html
        return jsonify(response), response['status_code']

    html = render_template("account/details.html", base_html="ajax.html", user=user)
    return jsonify({'html': html}), 200

@account_bp.route('/orders', methods=['GET'])
def orders():
    orders = _get_orders()

    if not request.args.get('partial') == "true":
        return render_template("account/orders.html", base_html="account/base.html", orders=orders)

    html = render_template('account/orders.html', base_html="ajax.html", orders=orders)
    return jsonify({'html': html}), 200

# dito pull ng data paedit nalang
def _get_orders():
    orders = [
        {'product_name': "Supreme T-Shirt", 'image_url': "supreme-tshirt.png", 'size': "M", 'color': "White", 'quantity': 1, 'status': "shipped", 'price': 2500, 'paymentmethod': "COD"},
        {'product_name': "Supreme T-Shirt", 'image_url': "supreme-tshirt.png", 'size': "M", 'color': "White", 'quantity': 1, 'status': "received", 'price': 2500, 'paymentmethod': "Bank Transfer"},
        {'product_name': "Supreme T-Shirt", 'image_url': "supreme-tshirt.png", 'size': "M", 'color': "White", 'quantity': 1, 'status': "to ship", 'price': 2500, 'paymentmethod': "GCash"},
        {'product_name': "Supreme T-Shirt", 'image_url': "supreme-tshirt.png", 'size': "M", 'color': "White", 'quantity': 1, 'status': "reviewed", 'price': 2500, 'paymentmethod': "GCash"},
        {'product_name': "Supreme T-Shirt", 'image_url': "supreme-tshirt.png", 'size': "M", 'color': "White", 'quantity': 1, 'status': "reviewed", 'price': 2500, 'paymentmethod': "Bank Transfer"}
    ]
    return orders

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

@account_bp.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('user_id', None)
    return redirect(url_for('home'))