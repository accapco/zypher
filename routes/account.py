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
    print("Received request for orders")
    user_id = session.get('user_id')

    print(f"User ID: {user_id}")

    # Validate user_id parameter
    if not user_id:
        return jsonify({'message': 'Missing user_id parameter'}), 400

    # Fetch orders from the model
    order_data = Account.get_orders(user_id)
    print(order_data)
    if order_data['status'] == 'error':
        return jsonify({'message': order_data['message']}), order_data['status_code']

    # Extract orders from the result, ensuring it's a list
    orders = list(order_data['order'])  # Convert tuple to list if necessary

    print(f"Orders for user {user_id}: {orders}")

    # Render template based on request type
    if request.args.get('partial') != "true":
        return render_template("account/orders.html", base_html="account/base.html", orders=orders)

    html = render_template('account/orders.html', base_html="ajax.html", orders=orders)
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

@account_bp.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('user_id', None)
    return redirect(url_for('home'))