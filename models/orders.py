from app import mysql
from flask_mysqldb import MySQLdb

class Orders:
    def getall():
        pass

    def get(order_id):
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('''
                SELECT * FROM Order_Summary 
                WHERE order_id = %s''', (order_id,)
                )
            order = cursor.fetchall()
            cursor.close()

            return {
                'order': order,
                'status': "success",
                'status_code': 200
            }
        except:
            return {
                'status': "error",
                'status_code': 500
            }

    def add(user_id, form, items):
        # process shipping info
        shipping_address = "{} {}, {}, {}, {}".format(
            form['f_name'], form['l_name'], 
            form['address'], form['city'], 
            form['postal']
            )
        payment_method = form['payment']
        if form['billing'] == 'same':
            billing_address = shipping_address
        else:
            billing_address = "{} {}, {}, {}, {}".format(
                form['f_name'], form['l_name'], 
                form['address'], form['city'], 
                form['postal']
                )
        # process price
        total = sum(float(i['price']) * int(i['quantity']) for i in items)
        try:
            # create order item
            cursor = mysql.connection.cursor()
            cursor.execute('''
                INSERT INTO Orders 
                (user_id, order_date, status, 
                total_amount, shipping_address) 
                VALUES (%s, NOW(), pending, %s, %s, %s)''', 
                (user_id, total, shipping_address)
                )
            mysql.connection.commit()
            order_id = cursor.lastrowid

            # attach each item to order
            for item in items:
                product_id = item['product_id']
                quantity = item['quantity']
                price = item['price']

                order_count = cursor.execute('''
                    SELECT COUNT(*) FROM Order_Summary 
                    WHERE product_id = %s''', (product_id,)
                    )
                order_count += 1
                order_number = f"ZYPHER{product_id}{str(order_count).zfill(3)}"

                cursor.execute('''
                    INSERT INTO Order_Summary 
                    (order_id, order_number, paymentmethod
                    product_id, quantity, price, created_at) 
                    VALUES (%s, %s, %s, %s, %s, NOW())''', 
                    (order_id, order_number, payment_method,
                    product_id, quantity, price)
                    )
                mysql.connection.commit()
            
            return {
                'order_id': order_id,
                'message': "Order created.",
                'status': "success",
                'status_code': 201
            }
        except Exception as e:
            return {
                'message': f"Order could not be created. {e}",
                'status': "error",
                'status_code': 500
            }