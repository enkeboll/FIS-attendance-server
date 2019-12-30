from flask import Blueprint, render_template, request

from app.models import EditableHTML, IDCard, Student, PunchIn

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
		id = int(request.args['id'])
	else:
		return "Error: No id field provided. Please specify an id."

	return f"Punch in recorded for card {id}"