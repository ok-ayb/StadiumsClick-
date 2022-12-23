from flask import Flask, render_template, request, session
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "stadiumsclick"
mysql=MySQL(app)


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html',username=session['username'])

@app.route('/terrain')
def ter_page():
    items= [
        {'id':1, 'name':'test', 'barcode':'89977788', 'price':10},
        {'id':1, 'name':'test', 'barcode':'89977788', 'price':12},
        {'id':1, 'name':'test', 'barcode':'89977788', 'price':16}
    ]
    return render_template("ter.html",items=items)

@app.route('/signeUp')
def signeUp_page():
    return render_template("signeUp.html")


@app.route('/club')
def club_page():
    return render_template("club.html")

@app.route('/Login',methods=['GET','POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM login WHERE user_name = %s AND password = %s', (username, password,))
        users = cursor.fetchone()
        if users:
            session['loggedin'] = True
            session['user_name'] = users['username']
            session['password'] = users['password']
            # Redirect to home page
            return 'Logged in successfully!'
        else:
            msg = 'Incorrect username/password!'
            return render_template('home.html', msg=msg)
        
    return render_template('login.html', msg=msg)

#pfa 
#------------------------------------------------------


@app.route('/addTer')
def add_Ter():
    return render_template("addTerrain.html")
