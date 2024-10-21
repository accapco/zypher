from app import mysql
import MySQLdb

import re

class Account:
    @staticmethod
    def get(user_id):
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM tbl_users WHERE user_id = %s', (user_id,))
            user = cursor.fetchone()
            return {
                'user': user, 
                'status': "success", 
                'status_code': 200
                }
        except:
            return {
                'message': "User could not be fetched.", 
                'status': "error",
                'status_code': 500
                }
    
    @staticmethod
    def update(form):
        username = form['username']   
        email = form['email']
        first_name = form['first_name']
        last_name = form['last_name']         
        phone = form['phone']
        address = form['address']
        city = form['city']
        state = form['state']
        zipcode = form['zipcode']
        country = form['country']
        user_id = form['userid']

        if email == '':
            return {
                'message': "Required fields are empty.", 
                'status': "warning", 
                'status_code': 400
                }
        elif not re.match(r'[A-Za-z0-9]+', username):
            return {
                'message': "Username must contain only characters and numbers.", 
                'status': "warning", 
                'status_code': 400
                }
        
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('''
                UPDATE tbl_users SET username=%s, email=%s, 
                first_name=%s, last_name=%s, phone=%s, 
                address=%s, city=%s, state=%s, 
                zipcode=%s, country=%s 
                WHERE user_id=%s''', 
                (username, email, 
                first_name, last_name, phone, 
                address, city, state, 
                zipcode, country, user_id)
                )
            mysql.connection.commit()
            return {
                'message': "Account has been updated.", 
                'status': "success", 
                'status_code': 200
                }
        except:
            return {
                'message': "Account could not be updated.", 
                'status': "error", 
                'status_code': 500
                }
        
    @staticmethod
    def register(form):
        userName = form['username']
        password = form['password']
        email = form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbl_users WHERE email = %s', (email,))
        account = cursor.fetchone()

        if account:
            return {
                'message': "Email has already been used.",
                'status': "warning",
                'status_code': 401
                }
        elif not (userName and password and email):
            return {
                'message': "Required fields are empty.",
                'status': "warning",
                'status_code': 401
                }
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            return {
                'message': "Please check your email address format.",
                'status': "warning",
                'status_code': 400
                }
        
        try:
            cursor.execute('''
                INSERT INTO tbl_users (username, email, password_hash) 
                VALUES (%s, %s, %s)''', 
                (userName, email, password)
                )
            mysql.connection.commit()
            cursor.execute('''
                SELECT * FROM tbl_users WHERE email = %s 
                AND password_hash = %s''', 
                (email, password,)
                )
            user = cursor.fetchone()
            return {
                'user': user,
                'message': "Account created.",
                'status': "success",
                'status_code': 201
                }
        except Exception:
            return {
                'message': "Error creating account.",
                'status': "error",
                'status_code': 500
                }
        
    @staticmethod
    def login(form):
        email = form['email']
        password = form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
            SELECT * FROM tbl_users 
            WHERE email = %s 
            AND password_hash = %s''', 
            (email, password)
            )
        user = cursor.fetchone()

        if user:
            return {
                'user': user,
                'message': "Successfully logged in.",
                'status': "success",
                'status_code': 200
                }
        else:
            return {
                'message': "Invalid credentials.",
                'status': "warning",
                'status_code': 401
                }

    @staticmethod
    def get_orders(user_id):
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('''
                SELECT order_id, order_date as date_of_purchase, 
                status, total_amount, shipping_address
                FROM Orders
                WHERE user_id = %s
                ORDER BY order_date DESC''', 
                (user_id,)
                )
            orders = cursor.fetchall() if cursor.rowcount > 0 else []

            for order in orders:
                cursor.execute('''
                    SELECT os.order_number, os.order_id, 
                    os.total_price, os.quantity, os.payment_method, 
                    p.image_url, p.product_name, p.size, p.color
                    FROM Order_Summary os
                    JOIN Products p ON os.product_id = p.product_id
                    WHERE order_id = %s
                    ORDER BY os.order_id ASC''', 
                    (order['order_id'],)
                    )
                items = cursor.fetchall()
                order['order_items'] = items
            cursor.close()

            return {
                'orders': orders,
                'status': "success",
                'status_code': 200
            }
        except Exception as e:
            return {
                'message': f"Error retrieving order: {e}",
                'status': "error",
                'status_code': 500
            }
        
    @staticmethod
    def get_order(user_id, order_id):
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('''
                SELECT order_id, order_date as date_of_purchase, 
                status, total_amount, shipping_address
                FROM Orders
                WHERE user_id = %s AND order_id = %s''', 
                (user_id, order_id)
                )
            order = cursor.fetchone()

            cursor.execute('''
                SELECT os.order_number, os.order_id, 
                os.total_price, os.quantity, os.payment_method, 
                p.image_url, p.product_name, p.size, p.color, p.price
                FROM Order_Summary os
                JOIN Products p ON os.product_id = p.product_id
                WHERE order_id = %s
                ORDER BY os.order_id ASC''', 
                (order['order_id'],)
                )
            items = cursor.fetchall()
            order['order_items'] = items
            cursor.close()

            return {
                'order': order,
                'status': "success",
                'status_code': 200
            }
        except Exception as e:
            return {
                'message': f"Error retrieving order: {e}",
                'status': "error",
                'status_code': 500
            }