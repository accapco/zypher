from app import mysql
from flask_mysqldb import MySQLdb

class Orders:
    @staticmethod
    def getall():
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('''
                SELECT o.order_id, o.order_date, o.status,
                o.total_amount, o.shipping_address, 
                u.first_name, u.last_name, u.username
                FROM Orders o 
                JOIN tbl_users u on o.user_id = u.user_id
                ORDER BY o.order_date DESC''')
            orders = cursor.fetchall()

            for order in orders:
                cursor.execute('''
                    SELECT os.quantity, os.payment_method, os.product_id,
                    os.order_number, os.contact_info, os.price, os.total_price,
                    p.product_name, p.image_url, p.size, p.color
                    FROM Order_Summary os
                    JOIN Products p ON os.product_id = p.product_id
                    WHERE os.order_id = %s''', 
                    (order['order_id'],)
                    )
                order['order_items'] = cursor.fetchall()

            cursor.close()

            return {
                'orders': orders,
                'status': "success",
                'status_code': 200
                }
        except Exception as e:
            return {
                'orders': [],
                'message': f"Error retrieving orders: {e}",
                'status': "error",
                'status_code': 500
                }
        
    @staticmethod
    def get(order_id):
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('''
                SELECT o.order_id, o.order_date, o.status,
                o.total_amount, o.shipping_address, 
                u.first_name, u.last_name, u.username
                FROM Orders o 
                JOIN tbl_users u on o.user_id = u.user_id
                WHERE o.order_id = %s''', 
                (order_id,)
                )
            order = cursor.fetchone()

            cursor.close()

            return {
                'order': order,
                'status': "success",
                'status_code': 200
                }
        except Exception as e:
            return {
                'order': None,
                'message': f"Error retrieving order: {e}",
                'status': "error",
                'status_code': 500
                }

    @staticmethod
    def add(user_id, form, items):
        # process shipping and billing information
        shipping_address = "{} {}, {}, {}, {}".format(
            form['f_name'], form['l_name'], 
            form['address'], form['city'], 
            form['postal']
        )
        print(shipping_address)
        if form.get('billing') != 'same':
            shipping_address = "{} {}, {}, {}, {}".format(
                form['f_name'], form['l_name'], 
                form['address'], form['city'], 
                form['postal'], form['region']
            )
        payment_method = form['payment']
        print(payment_method)
        billing_address = shipping_address if form['billing'] == 'same' else "{} {}, {}, {}, {}".format(
            form['f_name'], form['l_name'], 
            form['address'], form['city'], 
            form['postal']
        )

        contact_info = "{} (Phone: {})".format(form.get('contact'), form.get('phone'))
        print("Contact Info:", contact_info)
        # calculate total price
        total = sum(float(i['price']) * int(i['quantity']) for i in items)

        try:
            # create the order
            cursor = mysql.connection.cursor()
            cursor.execute('''
                INSERT INTO Orders 
                (user_id, order_date, status, total_amount, shipping_address) 
                VALUES (%s, NOW(), 'pending', %s, %s)
            ''', (user_id, total, shipping_address))
            mysql.connection.commit()
            order_id = cursor.lastrowid

            # create order summary for each product in the order
            for item in items:
                product_id = item['product_id']
                quantity = item['quantity']
                price = item['price']

                # count the existing orders for this product to generate the order number
                print(product_id, quantity, price)
                cursor.execute('''
                    SELECT COUNT(*) AS order_count FROM Order_Summary 
                    WHERE product_id = %s
                ''', (product_id,))
                order_count_row = cursor.fetchone()
                if order_count_row is not None:
                    order_count = order_count_row[0] + 1  # The count is at index 0
                else:
                    order_count = 1  # If no rows found, start with 1
                order_number = f"ZYPHER{product_id}00{order_count}"
                print("Generated Order Number:", order_number)

                # insert into Order_Summary
                cursor.execute('''
                    INSERT INTO Order_Summary 
                    (order_id, order_number, contact_info, shipping_address, 
                     payment_method, billing_address, product_id, quantity, price) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    order_id, order_number, contact_info, shipping_address,
                    payment_method, billing_address, product_id, quantity, price
                ))
                mysql.connection.commit()

            cursor.close()

            return {
                'order_id': order_id,
                'message': "Order created successfully.",
                'status': "success",
                'status_code': 201
            }

        except Exception as e:
            return {
                'message': f"Order creation failed: {e}",
                'status': "error",
                'status_code': 500
            }
        
    @staticmethod
    def schedule_shipment(order_id):
        return {
                'message': "Shipment scheduled.",
                'status': "success",
                'status_code': 200
            }