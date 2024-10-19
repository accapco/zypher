from flask import render_template, request, url_for, Blueprint, jsonify

from models.products import Products
from models.categories import Categories

products_bp = Blueprint('products', __name__)

@products_bp.route('/', methods=['GET'])
def getall():
    category = request.args.get("category")
    color = request.args.get("color")
    size = request.args.get("size")
    response = Products.getall(category=category, color=color, size=size)
    response['html'] = render_template("products/getall.html", products=response['products'])
    return jsonify(response), response['status_code']

@products_bp.route('/<int:product_id>', methods=['GET'])
def get(product_id):
    response = Products.get(product_id)
    return jsonify(response), response['status_code']

@products_bp.route('/archived', methods=['GET'])
def getall_archived():
    response = Products.getall(is_active=False)
    response['html'] = render_template("products/getall_archived.html", products=response['products'])
    return jsonify(response), response['status_code']

@products_bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        response = Products.add(request.form, request.files)
        response['redirect'] = url_for('.getall')
        return jsonify(response), response['status_code']
    
    categories = Categories.getall().get('categories')
    html = render_template('products/add.html', categories=categories)
    return jsonify({'html': html}), 200

@products_bp.route('/<int:product_id>/edit', methods=['GET', 'POST'])
def edit(product_id):
    if request.method == 'POST':
        response = Products.update(product_id, request.form, request.files)
        response['redirect'] = url_for('.getall')
        return jsonify(response), response['status_code']
    
    product = Products.get(product_id).get('product')
    categories = Categories.getall().get('categories')
    html = render_template("products/edit.html", product=product, categories=categories) 
    return jsonify({'html': html}), 200

@products_bp.route('/<int:product_id>/archive', methods=['GET', 'POST'])
def archive(product_id):     
    if request.method == 'POST':
        response = Products.archive(product_id)
        response['redirect'] = url_for('.getall')
        return jsonify(response), response['status_code']

    product = Products.get(product_id).get('product')
    html = render_template("products/archive.html", product=product)
    return jsonify({'html': html}), 200

@products_bp.route('/<int:product_id>/restore', methods=['GET', 'POST'])
def restore(product_id):
    if request.method == 'POST':
        response = Products.restore(product_id)
        response['redirect'] = url_for('.getall_archived')
        return jsonify(response), response['status_code']
    
    product = Products.get(product_id).get('product')
    html = render_template("products/restore.html", product=product)
    return jsonify({'html': html}), 200
