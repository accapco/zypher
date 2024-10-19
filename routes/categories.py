from flask import render_template, request, redirect, url_for, session, Blueprint, jsonify

from models.categories import Categories

categories_bp = Blueprint('categories', __name__)

@categories_bp.before_request
def verify_loggedin():
    if 'loggedin' not in session:
        return redirect(url_for('home'))

@categories_bp.route('/', methods =['GET', 'POST'])
def getall():
    category_tree = Categories.getall(as_tree=True).get('category_tree')
    html = render_template("categories/getall.html", category_tree=category_tree)
    return jsonify({'html': html}), 200

@categories_bp.route('/archived', methods =['GET', 'POST'])
def getall_archived():
    archived_categories = Categories.getall(is_archived=True).get('categories')
    html = render_template("categories/getall_archived.html", categories=archived_categories)
    return jsonify({'html': html}), 200

@categories_bp.route('/<int:parent_id>/add', methods=['GET', 'POST'])
def add(parent_id):
    if request.method == 'POST':
        response = Categories.add(request.form, parent_id)
        response['redirect'] = url_for('.getall')
        return jsonify(response), response['status_code']

    html = render_template('categories/add.html', parent_id=parent_id)
    return jsonify({'html': html}), 200

@categories_bp.route('/<int:category_id>/edit', methods=['GET', 'POST'])
def edit(category_id):
    if request.method == 'POST':
        response = Categories.update(category_id, request.form)
        response['redirect'] = url_for('.getall')
        return jsonify(response), response['status_code']
    
    category = Categories.get(category_id).get('category')
    categories = list( Categories.getall().get('categories') )
    categories.insert(0, {'category_name': "None", 'category_id': 0})

    html = render_template("categories/edit.html", category=category, parent_options=categories)
    return jsonify({'html': html}), 200

@categories_bp.route('/<int:category_id>/archive', methods=['GET', 'POST'])
def archive(category_id):
    if request.method == 'POST':
        response = Categories.archive(category_id)
        response['redirect'] = url_for('.getall')
        return jsonify(response), response['status_code']
    
    category = Categories.get(category_id).get('category')
    html = render_template("categories/archive.html", category=category)
    return jsonify({'html': html})

@categories_bp.route('/<int:category_id>/restore', methods=['GET', 'POST'])
def restore(category_id):
    if request.method == 'POST':
        response = Categories.restore(category_id)
        response['redirect'] = url_for('.getall_archived')
        return jsonify(response), response['status_code']

    category = Categories.get(category_id).get('category')
    html = render_template("categories/restore.html", category=category)
    return jsonify({'html': html}), 200

