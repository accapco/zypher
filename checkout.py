from flask import Flask, render_template,request, redirect, url_for, session, Blueprint, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import json
from app import mysql

checkout_bp = Blueprint('checkout', __name__)

@checkout_bp.before_request
def verify_loggedin():
    if 'loggedin' not in session:
        return redirect(url_for('home'))

@checkout_bp.route('/checkout', methods=['POST', 'GET'])
def checkout():
    if request.method == 'POST':
        # Get selected items from the form
        selected_items = request.form.get('selected_items')
        selected_items = json.loads(selected_items)

        # Calculate total
        total = sum(float(item['price']) * int(item['quantity']) for item in selected_items)

        # Fetch user details from the session
        user_id = session['user_id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT email, first_name, last_name, address, city FROM tbl_users WHERE user_id = %s', (user_id,))
        user_info = cursor.fetchone()
        cursor.close()

        return render_template("checkout/checkout.html", user_info=user_info, selected_items=selected_items, total=total)

    return render_template('checkout.html', selected_items=[], total=0)

