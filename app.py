from flask import Flask, render_template, url_for, redirect

app = Flask(__name__)

@app.route('/')
def index():    
    return redirect(url_for('.home'))

@app.route('/home')
def home():    
    return render_template('home.html')

@app.route('/catalog')
def catalog():    
    return render_template('catalog.html')

@app.route('/cart')
def cart():
    return render_template('cart.html')