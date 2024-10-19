from app import mysql
import MySQLdb

import re

class Users:
    @staticmethod
    def getall():
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM tbl_users')
            users = cursor.fetchall()
            return {
                'users': users,
                'status': "success",
                'status_code': 200
            }
        except:
            return {
                'users': [],
                'status': "error",
                'status_code': 500
            }
        
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
                'user': None,
                'message': "Could fetch user data.",
                'status': "error",
                'status_code': 500
                }

    @staticmethod
    def update(user_id, form):
        userName = form['username']   
        email = form['email']
        first_name = form['first_name']
        last_name = form['last_name']         
        phone = form['phone']
        address = form['address']
        city = form['city']
        state = form['state']
        zipcode = form['zipcode']
        country = form['country']

        if userName == '' or email == '':
            return {
                'message': "Required fields are empty.", 
                'status': "warning", 
                'status_code': 400
                }
        elif not re.match(r'[A-Za-z0-9]+', userName):
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
                address=%s, city=%s, state=%s, zipcode=%s, 
                country=%s WHERE user_id=%s''', 
                (userName, email, first_name, 
                 last_name, phone, address, 
                 city, state, zipcode, 
                 country, user_id)
                )
            mysql.connection.commit()
            return {
                'message': "User details updated.", 
                'status': "success", 
                'status_code': 200
                }
        except Exception as e:
            return {
                'message': "Error updating user: {}".format(e), 
                'status': "error", 
                'status_code': 500
                }
        
    @staticmethod
    def delete(user_id):
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('DELETE FROM tbl_users WHERE user_id = %s', (user_id,))
            mysql.connection.commit()
            return {
                'message': "User has been deleted.", 
                'status': "success", 
                'status_code': 200
                }
        except Exception as e:
            return {
                'message': "Error deleting user: {}".format(e), 
                'status': "error", 
                'status_code': 500
                }