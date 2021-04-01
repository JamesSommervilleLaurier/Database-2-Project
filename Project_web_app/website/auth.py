from flask import Blueprint, render_template, request, flash, redirect, url_for 
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from models import User
from . import connect_db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        email = request.form.get('email')
        password = request.form.get('password')
        
        mydb,mycursor = connect_db()
        mycursor.execute('SELECT * FROM user WHERE email = %s AND password = %s', (email, password,))

        account = mycursor.fetchone()

        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            flash('Logged in successfully!', category='success')
            return redirect(url_for('views.home'))
        else:
            flash('Incorrect email or password, try again.', category='error')


        #if user:
        #    if check_password_hash(user.password, password):
        #        flash('Logged in successfully!', category='success')
        #        login_user(user, remember=True)
        #        return redirect(url_for('views.home'))
        #    else:
        #        flash('Incorrect password, try again.', category='error')
        #else:
        #    flash('Email does not exist.', category='error')

    return render_template("login.html")


@auth.route('/logout')
def logout():
    
    logout_user()
    
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')


        mydb,mycursor = connect_db()
        mycursor.execute('SELECT * FROM user WHERE email = %s', (email,))
        user = mycursor.fetchone()

        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            #DATABASE STUFF OCCURS
            # ADD New User Query

            data_user = (email ,password1 ,first_name)
            add_user = ("INSERT INTO user "
                        "(email,password,first_name) "
                        "VALUES (%s, %s, %s)")
            
            mydb,mycursor = connect_db()
            mycursor.execute(add_user, data_user)
            mydb.commit()

            new_user = mycursor.lastrowid
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html") #,user=current_user)
