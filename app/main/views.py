from flask import Blueprint, current_app, render_template, request

from app import db
from app.models import EditableHTML, IDCard, Student, PunchIn
from ..utils import get_or_create


main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('main/index.html')


@main.route('/about')
def about():
    editable_html_obj = EditableHTML.get_editable_html('about')
    return render_template(
        'main/about.html', editable_html_obj=editable_html_obj)

@main.route('/punch-in', methods=['GET'])
def punch_in():
    if 'id' in request.args:
        serial_no = request.args['id']
        id_card = get_or_create(db.session, IDCard, serial_no=serial_no)
        print(id_card)
        current_app.logger.info(f'ID card scanned: {id_card}')
        punch_in = PunchIn(idcard_id=id_card.id)
        db.session.add(punch_in)
        db.session.commit()
        current_app.logger.info(f'Punch-in: {punch_in}')

        return f"Punch in recorded for card {serial_no}"

    else:
        return "Error: No id field provided. Please specify an id."

    