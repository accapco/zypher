from app import mysql
from flask_mysqldb import MySQLdb

class Orders:
    @staticmethod
    def getall():
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            
            cursor.execute('''
                SELECT o.order_id, o.order_date, o.status,
                o.total_amount, o.shipping_address, o.order_number, o.contact_info,
                o.payment_method, o.billing_address, u.first_name, u.last_name, u.username
                FROM Orders o 
                JOIN tbl_users u on o.user_id = u.user_id
                ORDER BY o.order_date DESC''')
            orders = cursor.fetchall()

            for order in orders:
                cursor.execute('''
                    SELECT os.quantity, os.product_id, os.price, os.total_price,
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
                o.total_amount, o.shipping_address, o.order_number,
                o.payment_method, o.billing_address, o.contact_info,
                u.first_name, u.last_name, u.username
                FROM Orders o 
                JOIN tbl_users u on o.user_id = u.user_id
                WHERE o.order_id = %s''', 
                (order_id,)
                )
            order = cursor.fetchone()

            cursor.execute('''
                SELECT os.quantity, os.price, os.total_price,
                p.product_name, p.size, p.image_url
                FROM Order_Summary os
                JOIN Products p ON os.product_id = p.product_id
                WHERE os.order_id = %s''',
                (order_id,)
                )
            order['order_items'] = cursor.fetchall()

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
        shipping_address = "{} {} {}, {}, {}".format(
            form['address'], form['city'], form['postal'], 
            form['region'], form['country']
        )

        if form.get('billing') != 'same':
            billing_address = "{} {} {}, {}, {}".format(
                form['billing_address'], form['billing_city'], 
                form['billing_postal'], form['billing_region'], 
                form['billing_country']
            )
        else:
            billing_address = shipping_address

        payment_method = form['payment']
        contact_info = "{} (Phone: {})".format(form.get('contact'), form.get('phone'))

        total = sum(float(i['price']) * int(i['quantity']) for i in items)

        try:
            cursor = mysql.connection.cursor()
            cursor.execute('''
                SELECT COUNT(*) AS order_count FROM Orders
            ''')
            order_count_row = cursor.fetchone()
            order_count = order_count_row[0] + 1 if order_count_row else 1
            order_number = f"ZYPHER{user_id}00{order_count}"

            cursor.execute('''
                INSERT INTO Orders 
                (user_id, order_date, status, total_amount, shipping_address, payment_method, 
                billing_address, order_number, contact_info) 
                VALUES (%s, NOW(), 'pending', %s, %s, %s, %s, %s, %s)
                ''', (user_id, total, shipping_address, payment_method, billing_address, order_number, contact_info))
            mysql.connection.commit()
            order_id = cursor.lastrowid

            for item in items:
                product_id = item['product_id']
                quantity = item['quantity']
                price = item['price']

                cursor.execute('''
                    INSERT INTO Order_Summary 
                    (order_id, shipping_address, product_id, quantity, price) 
                    VALUES (%s, %s, %s, %s, %s)''', 
                    (order_id, shipping_address, product_id, quantity, price)
                )
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
                'order_id': order_id,
                'message': "Order has been confirmed.",
                'status': "success",
                'status_code': 200
                }