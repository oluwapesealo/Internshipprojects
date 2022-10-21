from cgitb import text
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
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(text=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)

@views.route('/delete-note', methods=['POST'])
def delet_note():
    note = json.loads(request.text)
    noteId  = note['noteId']
    note = Note.quesry.get(noteId)

    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
            
    return jsonify({})
# views = Blueprint('views', __name__)

# @views.route('/login', methods=['GET', 'POST'])
# @login_required
# def home():
#     # language="english"
#     # company="Wemabank"
#     # Itemid=2
#     # price=10
#     # value={"language": language,"company": company,"Itemid": Itemid,"price": price}

#     # return json.dumps(value)
#     return render_template("home.html", user=current_user)





