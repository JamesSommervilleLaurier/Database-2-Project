from urllib.request import urlopen 
from bs4 import BeautifulSoup
from string import ascii_letters


general_items = ["water","salt","ground black pepper to taste","salt and pepper to taste","vegetable oil","olive oil"]


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
        print("Ingredient:",self.name,"\tQuantity:",self.quantity,"\tUnit:",self.unit,"\tPreparation:",self.prep,"\tGeneral Ingredient:",self.general)



for i in range(10001,10010):
    scrape_URL = "https://www.allrecipes.com/recipe/"+ str(i)+"/"
    
    try:
        request_page = urlopen(scrape_URL)
        page_html = request_page.read()
        request_page.close()

    except:
        print("404")

    html_soup = BeautifulSoup(page_html,'html.parser')

    recipe_name = html_soup.find("h1",class_="headline heading-content").get_text()
   
    review_num = html_soup.find("span",class_="review-star-text").get_text()
    review_num = review_num.strip()
    review_num = str(float(review_num.strip(ascii_letters+":")))

    ingredient_list = []

    measurements = html_soup.find_all("input",class_="checkbox-list-input")
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

        if ingredient[0] in general_items:
            general = "T"
        else:
            general = "F"
        
        if len(a)>1:
            ing = Ingredient_listing(a[0],ingredient[1],ingredient[2],a[1],general)
        else:
            ing = Ingredient_listing(a[0],ingredient[1],ingredient[2],"None",general)

        Ingredients_arr.append(ing)
    
    # create recipe object    

    recipe_object = Recipe(i,recipe_name,review_num,Ingredients_arr,directions_arr)


    #display
    recipe_object.display()
    print("")


import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="db2g1234",
  database="database2project"
)


mycursor = mydb.cursor()


mycursor.execute("SHOW TABLES")

for x in mycursor:
  print(x)

    
    


  

        

    



