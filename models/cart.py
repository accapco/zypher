from app import mysql
import MySQLdb

class Cart:
    @staticmethod
    def getall(user_id):
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('''
                SELECT cart_items.cart_item_id, cart_items.cart_id, cart_items.price, 
                    cart_items.quantity, products.product_id, products.product_name, 
                    products.image_url, products.color, products.size
                FROM cart_items
                INNER JOIN cart ON cart_items.cart_id = cart.cart_id
                INNER JOIN products ON cart_items.product_id = products.product_id
                WHERE cart.user_id = %s''', 
                (user_id,)
                )
            cart = cursor.fetchall()
            return {
                'cart': cart,
                'count': len(cart),
                'status': "success", 
                'status_code': 200
                }
        except:
            return {
                'cart': [], 
                'count': 0,
                'status': "error",
                'status_code': 500
                }
    
    @staticmethod
    def add(user_id, form):
        try:
            product_id = form['product_id']
            price = form['price']
            
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('''
                SELECT cart_id FROM Cart 
                WHERE user_id = %s''', 
                (user_id,)
                )
            cart = cursor.fetchone()

            if not cart:
                cursor.execute('''
                    INSERT INTO Cart (user_id) 
                    VALUES (%s)''', 
                    (user_id,)
                    )
                mysql.connection.commit()  
                cursor.execute('SELECT LAST_INSERT_ID() AS cart_id')
                cart = cursor.fetchone()

            cart_id = cart['cart_id']

            cursor.execute('''
                SELECT * FROM Cart_Items 
                WHERE product_id = %s AND cart_id = %s''', 
                (product_id, cart_id)
                )
            cart_item = cursor.fetchone()

            if cart_item:
                cursor.execute('''
                    UPDATE Cart_Items SET quantity = quantity + 1 
                    WHERE product_id = %s AND cart_id = %s''', 
                    (product_id, cart_id)
                    )
            else:
                cursor.execute('''
                    INSERT INTO Cart_Items (cart_id, product_id, quantity, price) 
                    VALUES (%s, %s, %s, %s)''', 
                    (cart_id, product_id, 1, price)
                    )
            mysql.connection.commit()
            return {
                'message': "Item added to cart.", 
                'status': "success",
                'status_code': 201
                }
        except:
            return {
                'message': "Error adding product.", 
                'status': "error",
                'status_code': 500
                }
    
    @staticmethod
    def remove(cart_id):
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('DELETE FROM cart_items WHERE cart_item_id = %s', (cart_id,)) 
            mysql.connection.commit()
            return {
                'message': "Item has been removed from the cart.", 
                'status': "info",
                'status_code': 200
                }
        except:
            return {
                'message': "Error removing item from the cart.", 
                'status': "error",
                'status_code': 500
                }