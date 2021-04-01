from flask import Flask
from flask_login import LoginManager
from flask_mysqldb import MySQL 
import re
from os import path
import mysql.connector


def connect_db():
    # global code to connect to the database

    try:
        mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="db2g1234",
        database="database2project"
        )
        mycursor = mydb.cursor(buffered=True)
        print('Database Connection Established!')

    except:
        print('Database Connection Failed!')

    return mydb,mycursor


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'

    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'db2g1234'
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_DB'] = 'database2project'
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'


    mysql = MySQL(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')


    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):

        select_user = """SELECT * FROM user WHERE user_id = %s"""
        
        mydb,mycursor = connect_db()
        mycursor.execute(select_user, (id,))
        user= mycursor.fetchone()

        return user

    return app

