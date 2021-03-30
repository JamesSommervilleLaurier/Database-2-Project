from urllib.request import urlopen 
from bs4 import BeautifulSoup
from string import ascii_letters

import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="database2project"
)


mycursor = mydb.cursor()

general_items = ["water","salt","ground black pepper","ground black pepper to taste","salt and pepper to taste","vegetable oil","olive oil","white sugar","all-purpose flour","ice water","boiling water"]
filler_terms = ["zesty","shredded","crushed","diced","chopped","prepared","freshly","fresh","ground","frozen","minced","uncooked","sliced","hard-boiled","grated"]

class Recipe:
    def __init__(self,recipe_id,recipe_name,recipe_review,ingredients_array,directions_array):
        self.recipe_id = recipe_id
        self.recipe_name = recipe_name
        self.recipe_review= recipe_review
        self.ingredients_array = ingredients_array
        self.num_ingredients = len(ingredients_array)
        self.directions_array = directions_array

        
    def display(self):
        print("Recipe ID:",self.recipe_id)
        print("Recipe:",self.recipe_name)
        #print("Rating:",self.recipe_review)
        print("Ingredients List:")
        for ingredient in self.ingredients_array:
            ingredient.display()
        #print("Directions:")
        #for direction in self.directions_array:
        #    print(direction)
        
class Ingredient_listing:
    def __init__(self,name,quantity,unit,prep,general):
        self.name = name
        self.quantity = quantity
        self.unit = unit
        self.prep = prep
        self.general = general

    def display(self):
        print("I:",self.name,"Q:",self.quantity,"U:",self.unit,"P:",self.prep,"G:",self.general)

recipes = [241001]
#recipes = [10009,16000,13600,17500,18300,19700,19216,19296,19346,19620,19680,
#19860,19920,11983,257918,233758,238691,279903,220323,14373,60037,228823,268249,
#82347,233287,221261,257305,241473,278776,22831,83557,11679,24771,79543,278271,
#163625,241001,283197,16895,244458,235449,54679,213109,9870,283664,47717,24239,32385,
# 25473,24264]
#for i in range(10003,90000,495):
for i in recipes:
    scrape_URL = "https://www.allrecipes.com/recipe/"+ str(i)+"/"
    
    try:
        request_page = urlopen(scrape_URL)
        page_html = request_page.read()
        request_page.close()

    except :
        print("404")
        continue
        

    html_soup = BeautifulSoup(page_html,'html.parser')

    recipe_name = html_soup.find("h1",class_="headline heading-content").get_text()
   
    review_num = html_soup.find("span",class_="review-star-text").get_text()
    review_num = review_num.strip()
    review_num = str(float(review_num.strip(ascii_letters+":")))

    ingredient_list = []

    measurements = html_soup.find_all("input",class_="checkbox-list-input")
    #if len(measurements) > 7:
        #continue
    for measurement in measurements:
        mtup = [measurement.get("data-ingredient"),measurement.get("data-init-quantity"),measurement.get("data-unit")]
        if mtup[0] != None:

            ingredient_list.append(mtup)
            

    directions = html_soup.find("ul",class_="instructions-section")
    instructions = directions.find_all("p")

    # Gather the Direction Information
    count = 1
    directions_arr =[]
    for direction in instructions:
        directions_arr.append("Step"+str(count)+": "+direction.get_text())
        count+=1

    # Gather the Ingredient Information 
    Ingredients_arr = []
    for ingredient in ingredient_list:

        a= ingredient[0].split(",")

        term = ""
        teststr = a[0]
        for word in filler_terms:
            temp = teststr
            teststr = teststr.replace( word , '')
            if temp != teststr :
                term = word.strip()
        
        a[0]= teststr.lstrip().lower()
        

        if ingredient[0] in general_items:
            general = "T"
        else:
            general = "F"
        
        if len(a)>1:
            if term != "":
                ing = Ingredient_listing(a[0],ingredient[1],ingredient[2],a[1]+","+term,general)
            else:
                ing = Ingredient_listing(a[0],ingredient[1],ingredient[2],a[1],general)
        else:

            if term != "":
                ing = Ingredient_listing(a[0],ingredient[1],ingredient[2],term,general)
            else:
                ing = Ingredient_listing(a[0],ingredient[1],ingredient[2],"None",general)

        Ingredients_arr.append(ing)
    
    # create recipe object    

    recipe_object = Recipe(i,recipe_name,review_num,Ingredients_arr,directions_arr)


    #display
    recipe_object.display()

    data_recipe = (int(recipe_object.recipe_id),
                    recipe_object.recipe_name,
                    recipe_object.recipe_review,
                    str(recipe_object.directions_array))
    add_recipe = ("INSERT INTO recipes "
                "(recipe_id,recipe_name, recipe_rating, directions) "
                "VALUES (%s, %s, %s, %s)")
    
    try:
        mycursor.execute(add_recipe, data_recipe)

    except:
        print("duplicate")
        continue
    
    recipeid = mycursor.lastrowid

    for ingredientobj in recipe_object.ingredients_array:

        data_r_ingredient = (int(recipeid),
                            ingredientobj.name,
                            ingredientobj.quantity,
                            ingredientobj.unit,
                            ingredientobj.prep,
                            ingredientobj.general)

        add_recipe_ingredient = ("INSERT INTO recipe_ingredients "
                    "(recipe_id,ingredient_name, quantity, unit, preparation, general) "
                    "VALUES (%s, %s, %s, %s, %s, %s)")
        
        mycursor.execute(add_recipe_ingredient, data_r_ingredient)

    mydb.commit()


    print("")

mycursor.close()
mydb.close()




    
    


  

        

    



