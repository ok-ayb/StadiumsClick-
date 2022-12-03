from flask import Flask, render_template

app = Flask(__name__)
@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/tairrain')
def ter_page():
    items= [
        {'id':1, 'name':'test', 'barcode':'89977788', 'price':10},
        {'id':1, 'name':'test', 'barcode':'89977788', 'price':12},
        {'id':1, 'name':'test', 'barcode':'89977788', 'price':16}
    ]
    return render_template('ter.html',items=items)