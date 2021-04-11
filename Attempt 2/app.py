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

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def get_users_fridge(user_id):
    
    mycursor = mysql.connection.cursor()
    mycursor.execute('SELECT * FROM fridge_contents WHERE user_id = %s ', ( user_id,))
    f_contents = mycursor.fetchall()
    return f_contents


def convert_unit(item_quantity,item_unit):
    #returns 0 for error quantities and for unquantifiable amounts 

    unquantifiable_units = ["thin slices","slice","slices","dashes","dash","pinch","splash","large","thick slices","medium","small","drops","bunch","recipe","(9 inch)","(1/4 inch thick) ring","(6 inch)","medium heads"]
    
    unit_units = ["clove","cloves","ear","ears","head","heads","stalk","stalks","leafs","leaves","units"]

    package_units = [
        ["(6 ounce) package",168],
        ["(8 ounce) package",224],
        ["(8 ounce) box",224],
        ["(6 ounce) can",168],
        ["(3 pound)", 1419],
        ["(16 ounce) package",448],
        ["(7 ounce) can",196],
        ["(16 ounce) container",448],
        ["(10 ounce) can", 280],
        ["(14 ounce) can",392],
        ["(8 ounce) can",224],
        ["(5 ounce) can",140],
        ["(15 ounce) can",420],
        ["(3.5 ounce) package",98],
        ["(.25 ounce) package",7]
        ["(4 ounce) cans",112]
        ["(10.75 ounce) cans",301]
        ["(5 ounce) jar",140]
        ["(3 ounce) package",84]
        ["(10.75 ounce) can",301]
        ["(18 ounce) package",504]
        ["(4 pound)",1,892]
        ["(1 ounce) squares",28]
        ["(3 ounce) packages",84]
    ]

    quantiffiable_units = [
        ["cup",237],
        ["cups",237],
        ["tablespoon",18], 
        ["tablespoons",18], 
        ["pound",473],
        ["pounds",473], 
        ["teaspoon",5],
        ["teaspoons",5],
        ["ounces",28],
        ["pint",473],
        ["lbs",473],
        ["oz",28],
        ["g",1],
        ["kg",1000],
        ["mL",1],
        ["L",1000]
    ]

    if item_unit in unquantifiable_units:
        return 0 , None

    if item_unit in unit_units:
        return item_quantity , "u"

    for unit in quantiffiable_units:
        if unit[0] == item_unit:
            if is_number(item_quantity):
                qnum = float(item_quantity)
                return item_quantity * unit[1] , "ml"

    for unit in package_units:
        if unit[0] == item_unit:
            if is_number(item_quantity):
                qnum = float(item_quantity)
                return item_quantity * unit[1] , "ml"
    
    return 0 , None
    

    
    
    



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
 

    fridge = get_users_fridge(session['id'])

    mycursor = mysql.connection.cursor()
    mycursor.execute('SELECT recipe_id,recipe_rating FROM recipes ')
    recipe_id_array = mycursor.fetchall()

    RID_score = []
    

    for recipe_id in recipe_id_array:
        RID_score.append([recipe_id[0],recipe_id[1],0])

    

    for arr in RID_score:
        score = 0
        for ingredient in fridge:

            
            mycursor.execute('SELECT count(*) FROM recipe_ingredients WHERE recipe_id = %s AND ingredient_name = %s ', ( arr[0],ingredient[1],))
            count = mycursor.fetchone()


            mycursor.execute("SELECT count(*) FROM recipe_ingredients WHERE recipe_id = %s AND ingredient_name LIKE %s", ( arr[0],'%'+ingredient[1]+'%',))
            count_pm = mycursor.fetchone()


            partialmatchcount = count_pm[0] - count[0]


            score += count[0] + (0.5* partialmatchcount)

        arr[2] = arr[1]*0.5*score 


    sorted_RIDs = sorted(RID_score, key=lambda x:x[2], reverse=True)

    print(sorted_RIDs)

    recipes = []
    counter = 0 
    for rid in sorted_RIDs:
        if counter <= 10:
            mycursor.execute('SELECT * FROM recipes WHERE recipe_id = %s ', ( rid[0],))
            recipe = mycursor.fetchone()
            counter += 1

            recipes.append(recipe)

    print(recipes)

    return render_template("recipes.html",recipes = recipes )


@app.route('/recipe_info',methods = ['POST','GET'])
def recipe_info():
    recipe_id = session["recipe_id"]


    mycursor = mysql.connection.cursor()
    mycursor.execute('SELECT * FROM recipes WHERE recipe_id = %s ', ( recipe_id,))
    recipe = mycursor.fetchone()

    mycursor.execute('SELECT * FROM recipe_ingredients WHERE recipe_id = %s ', ( recipe_id,))
    recipe_ingredients = mycursor.fetchall()

    recipe_rating = recipe[2]

    if recipe[3]:
        directions = ast.literal_eval(recipe[3])
    else:
        directions = []

                 
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