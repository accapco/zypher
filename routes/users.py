from flask import Blueprint, request, session, render_template, redirect, url_for, jsonify

from models.users import Users

users_bp = Blueprint('users', __name__)

@users_bp.before_request
def verify_loggedin():
    if 'loggedin' not in session:
        return redirect(url_for('home'))

@users_bp.route('/', methods=['GET', 'POST'])
def getall():
    users = Users.getall().get('users')
    html = render_template("users/getall.html", users=users)    
    return jsonify({'html': html}), 200

@users_bp.route('/<int:user_id>', methods=['GET', 'POST'])
def get(user_id): 
    user = Users.get(user_id).get('user')
    html = render_template("users/get.html", user=user)    
    return jsonify({'html': html}), 200

@users_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
def edit(user_id):
    if request.method == 'POST':
        response = Users.update(user_id, request.form)
        response['redirect'] = url_for('.getall')
        return jsonify(response)
    
    user = Users.get(user_id).get('user')
    html = render_template("users/edit.html", user=user)
    return jsonify({'html': html}), 200

@users_bp.route('/<int:user_id>/delete', methods=['GET', 'POST'])
def delete(user_id):
    if request.method == 'POST':
        response = Users.delete(user_id)
        response['redirect'] = url_for('.getall')
        return jsonify(response), response['status_code']
    
    user = Users.get(user_id).get('user')
    html = render_template("users/delete.html", user=user)   
    return jsonify({'html': html}), 200
