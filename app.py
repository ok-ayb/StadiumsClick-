from flask import Flask, render_template, request, session,  redirect
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = "super secret key"
bcrypt = Bcrypt(app)

app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "stadiumsclick"

mysql=MySQL(app)


@app.route('/terrain')
def ter_page():
    items= [
        {'id':1, 'name':'test', 'barcode':'89977788', 'price':10},
        {'id':1, 'name':'test', 'barcode':'89977788', 'price':12},
        {'id':1, 'name':'test', 'barcode':'89977788', 'price':16}
    ]
    return render_template("ter.html",items=items)

@app.route('/signeUp',methods=['POST','GET'])
def signeUp_page():
    #check if user is connected
    if session.get('loggedin', False) == True:
        return  redirect("/addTer")
    errors=[]
    if request.method == 'GET':
        return render_template("signeUp.html")
    else:
        email = request.form['email']
        nom = request.form['nom']
        password = request.form['password1']
        password_confirm = request.form['password2']
        #validation des données 
        if email == '':
            errors.append("SVP entrer votre mail")
        if nom == '':
            errors.append("SVP entrer votre nom")
        if password == '':
            errors.append("SVP entrer votre mot de passe")
        if password_confirm == '':
            errors.append("SVP confirmer votre mot de passe")
        if len(errors)>0 : 
            return render_template("signeUp.html",errors=errors)
        #hash password 
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        #Connection with DB
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO users VALUES (NULL, % s, % s, % s)', (nom, email, password_hash))
        mysql.connection.commit()
            #displaying message
        msg = 'You have successfully registered !'
        
        
        return render_template("Login.html",msg=msg)


@app.route('/club')
def club_page():
    return render_template("club.html")

@app.route('/Login',methods=['GET','POST'])
def login():
    #check if user is connected
    if session.get('loggedin', False) == True:
        return  redirect("/addTer")

    errors = []
    if request.method == 'GET':
        return render_template("Login.html")
    else:
        email = request.form['email']
        password = request.form['password']   
    #verification des donnée 
    if email == '':
        errors.append("SVP entrer votre mail")
    if password == '':
        errors.append("SVP entrer votre mot de passe")
    if len(errors)>0 : 
            return render_template("Login.html",errors=errors)
    #connection with DB
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE email = % s', [email])
    user = cursor.fetchone()
    if user and bcrypt.check_password_hash(user['password'], password):
            session['loggedin'] = True
            session['id'] = user['id']
            session['email'] = user['email']
            msg = 'Logged in successfully !'
            return redirect('/addTer')
    else:
            msg = 'Incorrect username / password !'
    return render_template('Login.html', msg = msg)


@app.route('/addTer')
def add_Ter():
    if session.get('loggedin', False) == False:
        return  redirect("/Login")
    return render_template("addTerrain.html")

@app.route('/logOut',methods=['GET','POST'])
def logout():
    session.pop('loggedin',None)
    session.pop('id',None)
    session.pop('email',None)
    return redirect('/Login')
