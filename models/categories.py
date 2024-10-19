from app import mysql
import MySQLdb

class Categories:
    @staticmethod
    def getall(is_archived=False, as_tree=False):
        def _build_category_tree(categories, parent_id=None):
            tree = []
            for category in categories:
                if category['parent_id'] == parent_id:
                    children = _build_category_tree(categories, category['category_id'])
                    if children:
                        category['children'] = children
                    else:
                        category['children'] = []
                    tree.append(category)
            return tree

        def _structure_categories_into_tree(categories):
            category_tree = _build_category_tree(categories, parent_id=None)
            return category_tree

        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('''
                SELECT * FROM categories 
                WHERE is_archived = %s''', 
                (is_archived,)
                )
            categories = cursor.fetchall()

            if as_tree:
                return {
                    'category_tree': _structure_categories_into_tree(categories),
                    'status': "success",
                    'status_code': 200
                    }
            else:
                return {
                    'categories': categories,
                    'status': "success",
                    'status_code': 200
                    }
        except:
            return {
                'status': "error",
                'status_code': 500
                }
    
    @staticmethod
    def get(category_id):
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('''
                SELECT * FROM categories 
                WHERE category_id = %s''', 
                (category_id,)
                )
            category = cursor.fetchone()
            return {
                'category': category,
                'status': "success", 
                'status_code': 200
                }
        except:
            return {
                'status': "error", 
                'status_code': 404
                }

    @staticmethod
    def add(form, parent_id=0):
        try:
            category_name = form['category_name']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            if parent_id == 0:
                parent_id = None
            else:
                cursor.execute('''
                    SELECT category_id 
                    FROM categories 
                    WHERE category_id = %s''', 
                    (parent_id,)
                    )
            cursor.execute('''
                INSERT INTO categories (category_name, parent_id) 
                VALUES (%s, %s)''', 
                (category_name, parent_id)
                )
            mysql.connection.commit()
            return {
                'message': "Created category.", 
                'status': "success", 
                'status_code': 201
                }
        except Exception as e:
            return {
                'message': "Error creating category: {}".format(e), 
                'status': "error", 
                'status_code': 500
                }

    @staticmethod   
    def update(category_id, form):
        try:
            category_name = form['category_name']
            parent_id = form['parent_id']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            if parent_id == 0:
                parent_id = "NULL"
            cursor.execute('''
                UPDATE categories 
                SET category_name = %s, parent_id = %s 
                WHERE category_id = %s''', 
                (category_name, parent_id, category_id)
                )
            mysql.connection.commit()
            return {
                'message': "Successfully updated this category", 
                'status': "success", 
                'status_code': 200
                }
        except Exception as e:
            return {
                'message': "Error updating this category: {}".format(e), 
                'status': "error", 
                'status_code' : 500
                } 

    @staticmethod
    def archive(category_id):
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('''
                UPDATE categories
                SET is_archived = TRUE
                WHERE category_id = %s''', 
                (category_id,)
                )
            mysql.connection.commit()
            return {
                'message': "Category has been archived.", 
                'status': "info", 
                'status_code': 200,
                }
        except:
            return {
                'message': "Could not archive this category.", 
                'status': "error", 
                'status_code': 500
                }

    @staticmethod
    def restore(category_id):
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('''
                UPDATE categories
                SET is_archived = FALSE
                WHERE category_id = %s''', 
                (category_id,)
                )
            mysql.connection.commit()
            return {
                'message': "Category has been restored.", 
                'status': "info", 
                'status_code': 200,
                }
        except:
            return {
                'message': "Could not restore this category.", 
                'status': "error", 
                'status_code': 500
                }

