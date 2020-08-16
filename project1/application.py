import os

from flask import Flask, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests
from flask import Flask, render_template, redirect, url_for, request, flash


#start a postgres database on heroku

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "8SriPN6sn5bllAOKVQIMGA", "isbns": "9781632168146"})
reply = res.json()


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/register", methods=['GET','POST'])
def register():
    session.clear()
    error = None
    username = None
    password = None

    userCheck = db.execute("SELECT * FROM users WHERE username = :username",
                           {"username":request.form.get("username")}).fetchone()

    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        if userCheck == None and (username and password) != '':
            # Insert register into DB
            db.execute("INSERT INTO users (username,password) VALUES (:username, :password)",
                                {"username":username, 
                                 "password":password})
            # Commit changes to database
            db.commit()
            return redirect(url_for('login'))
        
        if userCheck:
            error = 'Username taken. Please try another username.'
            
        if (username or password) == '':
            error = 'Empty Username or Password. Please enter a Username and Password.'


    
    return render_template('register.html', error=error)


@app.route("/welcome")
def welcome():
    render_template('welcome.html')

# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', None)
        password = request.form.get('password', None)
        
        # Query database postgres://bbilcrjmdqsefb:1792ea62a0f1684cafa24359decd4d31df2ac7f7a2bcf4bf9f86aad8254f5f2f@ec2-35-172-73-125.compute-1.amazonaws.com:5432/d6bt7imri7f5k9

        rows = db.execute("SELECT * FROM users WHERE username = :username",
                            {"username": username})
        result = rows.fetchone()
        


        # Ensure username exists and password is correct
        if result == None or result[2] != password:
            error = 'Invalid Credentials. Please try again.'
       
        if result[1] == username and result[2] == password:
            return render_template('welcome.html',username=username)
        
    return render_template('login.html', error=error)


@app.route("/logout")
def logout():
    session.clear()
    flash("Session Cleared. User Logged Out.") #it should be a message you want to see when the user makes the next request.
    return render_template('logout.html')



