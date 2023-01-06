from flask import Flask, render_template, request, session,  redirect
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import os
from flask import send_from_directory
from flask import jsonify
#import stripe


app = Flask(__name__)
app.secret_key = "super secret key"
bcrypt = Bcrypt(app)
#stripe_keys = {
 #       "secret_key": os.environ["STRIPE_SECRET_KEY"],
  #      "publishable_key": os.environ["STRIPE_PUBLISHABLE_KEY"],
    #}
#stripe.api_key = stripe_keys["secret_key"]

app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "stadiumsclick"
app.config['UPLOAD_FOLDER'] = "./upload"
app.config['MAX_CONTENT_PATH'] = 200000

mysql=MySQL(app)


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
            session['isadmin'] = user['isadmin']
            msg = 'Logged in successfully !'
            return redirect('/addTer')
    else:
            msg = 'Incorrect username / password !'
    return render_template('Login.html', msg = msg)

@app.route('/addTer',methods=['GET','POST'])
def add_Ter():
    errors=[]
    if session.get('loggedin', False) == False:
        return  redirect("/Login")
    if request.method == 'GET':
        return render_template("addTerrain.html")
    else:
        nom = request.form['nom']
        adresse = request.form['adresse']
        ville =  request.form.get('ville')
        prix =  request.form['prix']
        #verifier si l admin et connecter ou bien non 
        isadmin=session.get('isadmin',0)
        description = request.form['description']
        image = request.files['file']
    #verification des donnée 
    if nom == '':
        errors.append("SVP entrer le nom de tairrain")
    if adresse == '':
        errors.append("SVP entrer l addresse du tairrain")
    if ville == '':
        errors.append("SVP selectionner votre ville")
    if prix == '':
        errors.append("SVP entrer le prix de reservation")
    if description == '':
        errors.append("SVP entrer la description du tairrain")
    if len(errors)>0 : 
            return render_template("addTerrain.html",errors=errors)
    #upload file 
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)))
    image_name = secure_filename(image.filename)
    image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_name))
    #update DB
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT INTO terrains VALUES (NULL, % s, % s, % s, %s, %s, %s)', (nom, adresse, ville, prix, description,image_name))
    mysql.connection.commit()
            #displaying message
    msg = 'le tairrain est bien ajouter'
    return render_template("addTerrain.html",msg=msg,isadmin=isadmin)

@app.route('/logOut',methods=['GET','POST'])
def logout():
    session.pop('loggedin',None)
    session.pop('id',None)
    session.pop('email',None)
    return redirect('/Login')


@app.route('/listeTairrains',methods=['GET','POST'])
def listeTairrains():
    #verifier si l admin et connecter ou bien non 
    isadmin=session.get('isadmin',0)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM terrains')
    results = cursor.fetchall()
    return render_template('listeTerrains.html',liste=results,isadmin=isadmin)

@app.route('/reservation',methods=['GET','POST'])
def reservation():
    errors=[]
    if session.get('loggedin', False) == False:
        return  redirect("/Login")
    if request.method == 'GET':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM terrains')
        results = cursor.fetchall()
        return render_template("reservation.html",ter=results)
    else:
        user_id = session.get('id',0)
        isadmin=session.get('isadmin',0)
        tairrain =  request.form.get('tairrain')
        date_reservation = request.form['date_reservation']
        heure_reservation = request.form['heure_reservation']
        nom_reservation = request.form['nom_reservation']
        #verification des donnée 
    if tairrain == '':
        errors.append("SVP selectionner un  tairrain")
    if date_reservation == '':
        errors.append("SVP ajouter une date de reservation")
    if heure_reservation == '':
        errors.append("SVP ajouter l heur de reservation")
    if nom_reservation == '':
        errors.append("SVP entrer le nom de reservation")
    if len(errors)>0 : 
        return render_template("reservation.html",errors=errors)
    
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # had query ka ta7sseb ch7al men reservation 3andna ldak terrain f dik la date w heure
    cur.execute('SELECT COUNT(*) as deja_reserve FROM reservation WHERE id_terrain = %s AND date=%s and heure=%s ',(tairrain,date_reservation,heure_reservation )) # terrain machi tairrain
    result = cur.fetchone()
    # ka n7ato resultats f deja_reservé donc yla kant 3anda chi 7aja kbar men 
    if result["deja_reserve"] != 0:
         message = 'date et heure est deja reservé svr choisir une autre heure ou une autre date'
         return render_template("reservation.html",isadmin=isadmin,message=message)
    else:
        cur.execute('INSERT INTO reservation VALUES (NULL, %s,%s, %s, %s, %s)', (user_id, tairrain, date_reservation, heure_reservation, nom_reservation))
        mysql.connection.commit()
        msg = 'la reservation et bien effectuer'
        return render_template("reservation.html",msg=msg,isadmin=isadmin)



@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

@app.route('/addPost',methods=['GET','POST'])
def addPost():
    errors= []
    if session.get('loggedin', False) == False:
        return  redirect("/Login")
    if request.method == 'GET':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM reservation WHERE id_user = %s',[session['id']])
        results = cursor.fetchall()
        return render_template("post.html",liste=results)
    else: 
        user_id = session.get('id',0)
        #verifier si l admin et connecter ou bien non 
        isadmin=session.get('isadmin',0)
        reservation =  request.form.get('reservation')
        description = request.form['description']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
             #verification des donnée 
    if reservation == '':
        errors.append("SVP selectionner une  reservation")
    if description == '':
        errors.append("SVP ajouter une description")
    if len(errors)>0 : 
        return render_template("post.html",errors=errors)
    
    cur.execute('INSERT INTO post VALUES (NULL, %s, %s, %s)', (description, reservation, user_id))
    mysql.connection.commit()
    msg = 'le post est bien crée'
    return render_template("post.html", msg=msg, isadmin=isadmin)

@app.route('/listePost',methods=['GET','POST'])
def listePost():
    if session.get('loggedin', False) == False:
        return  redirect("/Login")
    #verifier si l admin et connecter ou bien non 
    isadmin=session.get('isadmin',0)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM reservation,post,terrains WHERE post.id_reservation=reservation.id  and reservation.id_terrain=terrains.id')
    results = cursor.fetchall()
    posts = []
    for match in results:
        cursor.execute('SELECT COUNT(id_user) as count From match_foot WHERE id_post = %s',[match['post.id']])
        count = cursor.fetchall()
        match['count'] = count[0]['count']
        #verifier si l utilisateur est deja inscrit dans un match 
        cursor.execute('SELECT COUNT(*) as count FROM match_foot WHERE id_user = %s AND id_post = %s',(session['id'],match['post.id']))
        deja_inscrit = cursor.fetchall()
        if deja_inscrit[0]['count'] > 0:
            match['deja_inscrit'] = 1
        else:
            match['deja_inscrit'] = 0
        posts.append(match)
    
        #cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #cur.execute('SELECT * FROM post,reservation,terrains WHERE post.id_reservation=reservation.id  and reservation.id_terrain=terrains.id')
    #image = cur.fetchall()
    return render_template("listePosts.html",liste=posts,isadmin=isadmin)


@app.route('/match',methods=['GET','POST'])
def match():
    post_id = request.form['test']
    user_id = session.get('id',0)
    #return jsonify(post_id)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT INTO match_foot VALUES (NULL, %s, %s)', (post_id, user_id))
    mysql.connection.commit()
    msg="vous avez rejoindre cette equipe, Merci ^^"
    return render_template("listePosts.html",msg=msg)

@app.route('/delete',methods=['GET','POST'])
def delete_match():
    post_id = request.form['ok']
    #return jsonify(post_id)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM match_foot WHERE id_user = %s AND id_post = %s',(session['id'],post_id))
    mysql.connection.commit()
        #return jsonify(test)
    message='suppression bien effectuer'
    return render_template("listePosts.html", message=message)


