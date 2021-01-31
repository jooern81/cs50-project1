import os

from flask import Flask, session, jsonify, render_template
from flask_session import Session
from sqlalchemy import create_engine, select, MetaData, Table
from sqlalchemy.orm import scoped_session, sessionmaker
import requests
from flask import Flask, render_template, redirect, url_for, request, flash
import psycopg2
from jinja2 import Environment, FileSystemLoader, PackageLoader,Template

# start a postgres database on heroku

app = Flask(__name__)
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
host = "ec2-35-172-73-125.compute-1.amazonaws.com"
database = "d6bt7imri7f5k9"
user = "bbilcrjmdqsefb"
port = "5432"
password = "1792ea62a0f1684cafa24359decd4d31df2ac7f7a2bcf4bf9f86aad8254f5f2f"
URI = "postgres://bbilcrjmdqsefb:1792ea62a0f1684cafa24359decd4d31df2ac7f7a2bcf4bf9f86aad8254f5f2f@ec2-35-172-73-125.compute-1.amazonaws.com:5432/d6bt7imri7f5k9"

# Heroku CLI
# heroku pg:psql postgresql-silhouetted-61094 --app supermarketsimulator

engine = create_engine(
    'postgres://bbilcrjmdqsefb:1792ea62a0f1684cafa24359decd4d31df2ac7f7a2bcf4bf9f86aad8254f5f2f@ec2-35-172-73-125.compute-1.amazonaws.com:5432/d6bt7imri7f5k9')
meta = MetaData()

try:
    connection = psycopg2.connect(user=user,
                                  password=password,
                                  host=host,
                                  port=port,
                                  database=database)

except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL", error)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/table/<table_name>", methods=['GET', 'POST'])  # take url following /table/ as input
def render_table(table_name):
    if request.method == 'GET':
        cursor = connection.cursor()  # print some of the newly added table's details
        postgreSQL_select_Query = "select * from {}".format(table_name)
        cursor.execute(postgreSQL_select_Query)
        table = cursor.fetchall()
        cursor.close()

    return jsonify(table)


# @app.route("/register", methods=['GET','POST'])
# def register():

# if request.method == 'POST':
#     username = request.form.get('username', '')
#     password = request.form.get('password', '')

#     if userCheck == None and (username and password) != '':
#         # Insert register into DB
#         db.execute("INSERT INTO users (username,password) VALUES (:username, :password)",
#                             {"username":username,
#                              "password":password})
#         # Commit changes to database
#         db.commit()
#         return redirect(url_for('login'))

#     if userCheck:
#         error = 'Username taken. Please try another username.'

#     if (username or password) == '':
#         error = 'Empty Username or Password. Please enter a Username and Password.'

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
            return render_template('welcome.html', username=username)

    return render_template('login.html', error=error)


@app.route("/tableformat", methods=['GET', 'POST'])
def render_table_details():
    cursor = connection.cursor()  # print some of the newly added table's details
    postgreSQL_select_Query = "select * from {} order by product".format("basedata_supplierquotes_table")
    cursor.execute(postgreSQL_select_Query)
    data = cursor.fetchall()
    cursor.close()
    return render_template("tableformat.html", output_data = data)

@app.route("/logout")
def logout():
    session.clear()
    flash(
        "Session Cleared. User Logged Out.")  # it should be a message you want to see when the user makes the next request.
    return render_template('logout.html')
