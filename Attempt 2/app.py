from flask import Flask, Blueprint, render_template, request, flash, redirect, url_for,session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from flask_mysqldb import MySQL
import json
import ast


app = Flask(__name__)

app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'

app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'db2g1234'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_DB'] = 'database2project'


mysql = MySQL(app)


def get_users_fridge(user_id):
    
    mycursor = mysql.connection.cursor()
    mycursor.execute('SELECT * FROM fridge_contents WHERE user_id = %s ', ( user_id,))
    f_contents = mycursor.fetchall()
    return f_contents


# HOME ROUTE

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':

        item = request.form.get('item')
        item = item.lower()
        quantity = request.form.get('quan')
        unit = request.form.get('unit')

        if len(item) < 1:
            flash('Thats not an ingredient!', category='error')
        else:

            #INSERT IGNREDIENT QUERY
            data_f_content = (item, quantity, unit, session['id'])

            insert_fridge_content = ("INSERT INTO fridge_contents "
                    "(item,quantity,unit,user_id) "
                    "VALUES (%s, %s, %s, %s)")

            mycursor = mysql.connection.cursor()
            mycursor.execute(insert_fridge_content, data_f_content)
            mysql.connection.commit()

            flash('Ingredient added!', category='success')

    notes =  get_users_fridge(session['id'])
    return render_template("home.html",user = session['id'] , notes = notes)


@app.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)

    noteId = note['noteId']

    mycursor = mysql.connection.cursor()
    mycursor.execute("DELETE FROM fridge_contents WHERE id = %s",(noteId,))
    mysql.connection.commit()
    
    notes =  get_users_fridge(session['id'])
    return render_template("home.html",user = session['id'] , notes = notes)

@app.route('/recipes', methods=['GET'])
def recipes():
    # route to display tabulated basic recipe data  
    #recipes = [["recipe name" , "recipe basic info"],["recipe name 2" , "recipe basic info 2"]]

    mycursor = mysql.connection.cursor()
    mycursor.execute('SELECT * FROM recipes LIMIT 20')
    recipes = mycursor.fetchall()
    
    print(recipes)

    return render_template("recipes.html",recipes = recipes )


@app.route('/recipe_info',methods = ['POST','GET'])
def recipe_info():
    recipe_id = session["recipe_id"]

    print (recipe_id)

    mycursor = mysql.connection.cursor()
    mycursor.execute('SELECT * FROM recipes WHERE recipe_id = %s ', ( recipe_id,))
    recipe = mycursor.fetchone()

    mycursor.execute('SELECT * FROM recipe_ingredients WHERE recipe_id = %s ', ( recipe_id,))
    recipe_ingredients = mycursor.fetchall()

    recipe_rating = recipe[2]

    print("r3" ,recipe[3])
    if recipe[3]:
        directions = ast.literal_eval(recipe[3])
    else:
        directions = []

    print(recipe[1])

    for ing in recipe_ingredients:

        print(ing[2])

    for direction in directions:
        print(direction)




    return render_template("recipe_info.html",recipe_name = recipe[1],recipe_rating = recipe_rating,ingredients = recipe_ingredients, directions = directions)



@app.route('/get_recipe_info', methods=['POST'])
def get_recipe_info():
    if request.method == 'POST':

        recipe = json.loads(request.data)
        session['recipe_id'] = recipe['recipeId']

        return jsonify({})
    

# AUTHENTICATION ROUTES

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        email = request.form.get('email')
        password = request.form.get('password')
        
        mycursor = mysql.connection.cursor()
        mycursor.execute('SELECT * FROM user WHERE email = %s AND password = %s', (email, password,))

        account = mycursor.fetchone()

        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account[0]
            session['email'] = email
            # Redirect to home page
            flash('Logged in successfully!', category='success')
            return redirect(url_for('home') )
        else:
            flash('Incorrect email or password, try again.', category='error')

    return render_template("login.html")


@app.route('/logout')
def logout():

    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    
    return redirect(url_for('login'))


@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')


        mycursor = mysql.connection.cursor()
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
            
            mycursor = mysql.connection.cursor()
            mycursor.execute(add_user, data_user)
            mysql.connection.commit()

            user_id = mycursor.lastrowid

            session['loggedin'] = True
            session['id'] = user_id
            session['email'] = email
            
            flash('Account created!', category='success')
            return redirect(url_for('home'))

    return render_template("sign_up.html")



if __name__ == '__main__':
    app.run(debug=True)