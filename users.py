from flask import Blueprint, request, session, render_template, redirect, url_for, jsonify
import MySQLdb.cursors
import re

from app import mysql

users_bp = Blueprint('users', __name__)

@users_bp.before_request
def verify_loggedin():
    if 'loggedin' not in session:
        return redirect(url_for('home'))

@users_bp.route('/', methods=['GET', 'POST'])
def getall():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_users')
    users = cursor.fetchall()
    users_html = render_template("users/getall.html", users=users)    
    return jsonify({'html': users_html})

@users_bp.route('/<int:user_id>', methods=['GET', 'POST'])
def get(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_users WHERE user_id = %s', (user_id,))
    user = cursor.fetchone()
    user_html = render_template("users/get.html", user=user)    
    return jsonify({'html': user_html})

@users_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
def edit(user_id):
    msg = ''    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbl_users WHERE user_id = %s', (user_id,))
    user = cursor.fetchone()

    if request.method == 'POST' and 'username' in request.form and 'email' in request.form:
        # Get form data
        userName = request.form['username']   
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']         
        phone = request.form['phone']
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        zipcode = request.form['zipcode']
        country = request.form['country']

        if not re.match(r'[A-Za-z0-9]+', userName):
            msg = 'Username must contain only characters and numbers!'
        else:
            cursor.execute(
                'UPDATE tbl_users SET username=%s, email=%s, first_name=%s, last_name=%s, phone=%s, address=%s, city=%s, state=%s, zipcode=%s, country=%s WHERE user_id=%s', 
                (userName, email, first_name, last_name, phone, address, city, state, zipcode, country, user_id)
            )
            mysql.connection.commit()
            msg = 'User details have been updated'
    elif request.method == 'POST':
        msg = 'Some required fields are empty'
    edit_html = render_template("users/edit.html", user=user)    
    return jsonify({'html': edit_html, 'message': msg})

@users_bp.route('/<int:user_id>/delete', methods=['GET', 'POST'])
def delete(user_id):
    msg = ''
    delete_html = None
    if request.method == 'POST':
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('DELETE FROM tbl_users WHERE user_id = %s', (user_id,))
            mysql.connection.commit()
            msg = 'User deleted successfully'
        except Exception as e:
            msg = 'Error deleting user'
        return jsonify({'message': msg})
    else:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_users WHERE user_id = %s', (user_id,))
        user = cursor.fetchone()
        delete_html = render_template("users/delete.html", user=user)   
        return jsonify({'html': delete_html})