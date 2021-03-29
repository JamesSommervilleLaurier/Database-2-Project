from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
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
            new_note = Note(item=item,quantity=quantity,unit=unit, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Ingredient added!', category='success')

    return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']

    #DATABASE STUFF OCCURS
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})
