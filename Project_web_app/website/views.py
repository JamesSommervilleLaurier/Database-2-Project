from flask import Blueprint, render_template, request, flash, jsonify,session

#from .models import Note
from . import connect_db

import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':

        
        item = request.form.get('item')
        item = item.lower()
        quantity = request.form.get('quan')
        unit = request.form.get('unit')

        if len(item) < 1:
            flash('Thats not an ingredient!', category='error')
        else:
            #DATABASE STUFF OCCURS
            #submit a new ingredient query

            data_f_content = (item,
                            quantity,
                            unit,
                            current_user.id)

            insert_fridge_content = ("INSERT INTO fridge_contents "
                    "(item,quantity,unit,user_id) "
                    "VALUES (%s, %s, %s, %s)")

            mydb,mycursor = connect_db()
            mycursor.execute(insert_fridge_content, data_f_content)
            mydb.commit()
            #new_note = Note(item=item,quantity=quantity,unit=unit, user_id=current_user.id)
            #db.session.add(new_note)
            #db.session.commit()
            flash('Ingredient added!', category='success')

    return render_template("home.html")


@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']

    #DATABASE STUFF OCCURS
    #delete the note 

    data_d_f_content = (noteId)

    delete_fridge_ingredient = ("DELETE FROM fridge_contents WHERE id = "
                                "(id) "
                                "VALUES (%s)")

    mydb,mycursor = connect_db()
    mycursor.execute(delete_fridge_ingredient, data_d_f_content)
    mydb.commit()

    #note = Note.query.get(noteId)

    #if note:
    #    if note.user_id == current_user.id:
    #        db.session.delete(note)
    #        db.session.commit()

    return jsonify({})
