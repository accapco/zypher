from flask import Flask, render_template,request, redirect, url_for, session, Blueprint, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from app import mysql

categories_bp = Blueprint('categories', __name__)

@categories_bp.before_request
def verify_loggedin():
    if 'loggedin' not in session:
        return redirect(url_for('home'))

def build_category_tree(categories, parent_id=None):
    tree = []
    for category in categories:
        if category['parent_id'] == parent_id:
            children = build_category_tree(categories, category['category_id'])
            if children:
                category['children'] = children
            else:
                category['children'] = []
            tree.append(category)
    return tree

def structure_categories_into_tree(categories):
    category_tree = build_category_tree(categories, parent_id=None)
    return category_tree

def _get_categories():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM categories WHERE is_archived = FALSE')
    categories = cursor.fetchall()
    return categories

@categories_bp.route('/', methods =['GET', 'POST'])
def getall():
    categories = _get_categories()
    category_tree = structure_categories_into_tree(categories)
    categories_html = render_template("categories/getall.html", category_tree=category_tree)
    return jsonify({'html': categories_html, 'category_tree': category_tree})

@categories_bp.route('/archived', methods =['GET', 'POST'])
def getall_archived():
    archived_categories = _get_archived_categories()
    categories_html = render_template("categories/getall_archived.html", categories=archived_categories)
    return jsonify({'html': categories_html, 'archived_categories': archived_categories})

@categories_bp.route('/<int:category_id>/add', methods=['GET', 'POST'])
def add(category_id):
    msg = ""
    if request.method == 'POST':
        category_name = request.form['category_name']
        parentid = category_id
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if parentid == 0:
            parentid = None
        else:
            cursor.execute('SELECT category_id FROM categories WHERE category_id = %s', (parentid,))
        cursor.execute('INSERT INTO categories (category_name, parent_id) VALUES (%s, %s)', (category_name, parentid))
        mysql.connection.commit()
        msg = 'You have successfully created a category!'
    add_category_html = render_template('categories/add.html', category_id=category_id)
    return jsonify({'html': add_category_html, 'message': msg, 'redirect': url_for('.getall')})

@categories_bp.route('/<int:category_id>/edit', methods=['GET', 'POST'])
def edit(category_id):
    msg = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM categories where category_id = %s', (category_id,))
    category = cursor.fetchone()
    if request.method == 'POST':
        category_name = request.form['category_name']
        parentid = request.form['parent_id']
        if parentid == 0:
            parentid = "Null"
        cursor.execute('UPDATE categories SET category_name = %s, parent_id = %s WHERE category_id = %s', (category_name, parentid, category_id))
        mysql.connection.commit()
        msg = 'You have successfully updated a category!'
    categories = list(_get_categories())
    categories.insert(0, {'category_name': "None", 'category_id': 0})
    edit_category_html = render_template("categories/edit.html", category=category, parent_options=categories)
    return jsonify({'html': edit_category_html, 'message': msg, 'redirect': url_for('.getall')})

def _get_archived_categories():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM categories WHERE is_archived = TRUE')
    categories = cursor.fetchall()
    return categories

@categories_bp.route('/<int:category_id>/archive', methods=['GET', 'POST'])
def archive(category_id):
    msg = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM Categories WHERE category_id = %s', (category_id,))
    category = cursor.fetchone()
    if request.method == 'POST':
        cursor.execute('''
            UPDATE categories
            SET is_archived = TRUE
            WHERE category_id = %s
        ''', (category_id,))
        mysql.connection.commit()
        msg = 'Successfully archived this category.'
    archive_category_html = render_template("categories/archive.html", category=category)
    return jsonify({'html': archive_category_html, 'message': msg, 'redirect': url_for('.getall')})

@categories_bp.route('/<int:category_id>/restore', methods=['GET', 'POST'])
def restore(category_id):
    msg = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM categories WHERE category_id = %s', (category_id,))
    category = cursor.fetchone()
    if request.method == 'POST':
        try:
            cursor.execute('''
                UPDATE categories
                SET is_archived = FALSE
                WHERE category_id = %s
            ''', (category_id,))
            mysql.connection.commit()
            msg = 'Successfully restored this category.'
        except Exception as e:
            msg = 'Error: [{}]'.format(e)
    else:
        msg = 'Category not found or already unarchived.'
    restore_category_html = render_template("categories/restore.html", category=category)
    return jsonify({'html': restore_category_html, 'message': msg, 'redirect': url_for('.getall_archived')})

