from app import app, mysql
import MySQLdb
from werkzeug.utils import secure_filename

import os

class Products:
    @staticmethod
    def getall(category=None, color=None, size=None, is_active=True):
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            # Initialize base query and conditions
            base_query = f'''
                SELECT p.*, c.category_name 
                FROM products p 
                JOIN categories c ON p.category_id = c.category_id 
                WHERE p.is_active = {str(is_active)}
                '''
            conditions = []
            params = []
            # Filter by category (recursive category tree)
            if category:
                cursor.execute('''
                    WITH RECURSIVE CategoryTree AS (
                        SELECT category_id, category_name, parent_id
                        FROM categories
                        WHERE category_id = %s
                        
                        UNION ALL
                        
                        SELECT c.category_id, c.category_name, c.parent_id
                        FROM categories c
                        INNER JOIN CategoryTree ct ON c.parent_id = ct.category_id
                    )
                    SELECT category_id FROM CategoryTree
                ''', (category,))
                
                related_categories = cursor.fetchall()
                category_ids = [row['category_id'] for row in related_categories]
                
                if category_ids:
                    format_strings = ','.join(['%s'] * len(category_ids))
                    conditions.append(f'c.category_id IN ({format_strings})')
                    params.extend(category_ids)
            # Filter by color
            if color:
                conditions.append('p.color = %s')
                params.append(color)
            # Filter by size
            if size:
                conditions.append('p.size = %s')
                params.append(size)
            if conditions:
                base_query += ' AND ' + ' AND '.join(conditions)
            cursor.execute(base_query, tuple(params))
            products = cursor.fetchall()
            return {
                'products': products,
                'status': "success",
                'status_code': 200
            }
        except:
            return {
                'products': [],
                'status': "error",
                'status_code': 500
            }
        
    @staticmethod
    def get(product_id):
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('''
                SELECT * FROM products 
                WHERE product_id = %s
                ''', (product_id,)
                )
            product = cursor.fetchone()
            if product:
                # Fetch product images
                cursor.execute('''
                    SELECT image_url FROM product_images 
                    WHERE product_id = %s''', 
                    (product_id,)
                    )
                images = cursor.fetchall()
                product['images'] = images
                return {
                    'product': product,
                    'message': "Successfully fetched product.",
                    'status': "success",
                    'status_code': 200
                    }
            else:
                return {
                    'message': "Product not found.",
                    'status': "error",
                    'status_code': 404
                    }
        except:
            return {
            'message': "Internal server error.",
            'status': "error",
            'status_code': 500
            }

    @staticmethod
    def colors():
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('''
                SELECT DISTINCT color
                FROM products
                WHERE products.is_active = TRUE'''
            )
            colors = cursor.fetchall()
            return {
                'colors': [c['color'] for c in colors],
                'status': "success",
                'status_code': 200
                }
        except:
            return {
                'colors': [],
                'status': "error",
                'status_code': 500
                }

    @staticmethod
    def sizes():
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('''
                SELECT DISTINCT size
                FROM products
                WHERE products.is_active = TRUE'''
            )
            sizes = cursor.fetchall()
            return {
                'sizes': [s['size'] for s in sizes],
                'status': "success",
                'status_code': 200
                }
        except:
            return {
                'sizes': [],
                'status': "error",
                'status_code': 500
                }

    @staticmethod
    def add(form, files):
        def _allowed_file(filename):
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

        categoryid = form['category_id']
        productname = form['product_name']
        description = form['description']
        price = form['price']
        stockqty = form['stock_quantity']
        size = form['size']
        color = form['color']
        images = files.getlist('images')

        if images and _allowed_file(images[0].filename):
            try:
                first_image = images[0]
                filename = secure_filename(first_image.filename)
                image_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
                first_image.seek(0)
                first_image.save(image_path)
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('''
                    INSERT INTO products 
                    (category_id, product_name, description, 
                    price, stock_quantity, size, color, image_url) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
                    (categoryid, productname, description, 
                     price, stockqty, size, color, filename)
                    )
                product_id = cursor.lastrowid
                for image in images:
                    if _allowed_file(image.filename):
                        filename = secure_filename(image.filename)
                        image_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
                        image.seek(0)
                        image.save(image_path)
                        cursor.execute('''
                            INSERT INTO product_images 
                            (product_id, image_url) VALUES (%s, %s)''', 
                            (product_id, filename)
                            )
                mysql.connection.commit()
                return {
                    'message': "Successfully added product.", 
                    'status': "success",
                    'status_code': 201 
                    }
            except Exception as e:
                return {
                    'message': "Error occured when adding product: {}".format(e), 
                    'status': "error",
                    'status_code': 500
                    }
        else:
            return {
                'message': "Atleast one image is required", 
                'status': "warning",
                'status_code': 400
                }
        
    @staticmethod
    def update(product_id, form, files):
        categoryid = form['category_id']
        productname = form['product_name']
        description = form['description']
        price = form['price']
        stockqty = form['stock_quantity']
        size = form['size']
        color = form['color']
        image_file = files.get('image') 

        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            if image_file:
                image_filename = secure_filename(image_file.filename)
                image_file.save(os.path.join('uploads', image_filename))  # Save the file
                cursor.execute('''
                    UPDATE products SET category_id = %s, product_name = %s, 
                    description = %s, price = %s, stock_quantity = %s, 
                    size = %s, color = %s, image = %s 
                    WHERE product_id = %s''', 
                    (categoryid, productname, description, 
                     price, stockqty, size, 
                     color, image_filename, product_id)
                    )
            else:
                cursor.execute('''
                    UPDATE products SET category_id = %s, product_name = %s, 
                    description = %s, price = %s, stock_quantity = %s, 
                    size = %s, color = %s WHERE product_id = %s''', 
                    (categoryid, productname, description, 
                     price, stockqty, size, color, product_id)
                    )
            mysql.connection.commit()
            return {
                'message': "Product details updated.", 
                'status': "info", 
                'status_code': 200
                }
        except Exception as e:
            return {
                'message': "Error updating product: {}".format(e), 
                'status': "error", 
                'status_code': 500
                }
        
    @staticmethod
    def archive(product_id):
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('''
                UPDATE products
                SET is_active = FALSE
                WHERE product_id = %s''', 
                (product_id,)
                )
            mysql.connection.commit()
            return {
                'message': "Product has been archived.", 
                'status': "info", 
                'status_code': 200,
                }
        except Exception as e:
            return {
                'message': "Error occured when archiving product: {}".format(e), 
                'status': "error", 
                'status_code': 500,
                }
        
    @staticmethod
    def restore(product_id):
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('''
                UPDATE products
                SET is_active = TRUE
                WHERE product_id = %s''', 
                (product_id,)
                )
            mysql.connection.commit()
            return {
                'message': "Product restored.", 
                'status': "info",
                'status_code': 200,
                }
        except Exception as e:
            return {
                'message': "Product could not be restored. {}".format(e), 
                'status': "error",
                'status_code': 500
                }