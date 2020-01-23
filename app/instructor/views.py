import csv
from io import StringIO

from flask import (
    Blueprint,
    Markup,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for
)
from flask_login import current_user, login_required
from flask_rq import get_queue
from werkzeug.utils import secure_filename

from app import db
from app.instructor.forms import (
    ChangeStudentCohortForm,
    ChangeStudentEmailForm,
    NewCohortForm,
    NewStudentForm,
    StudentUploadForm
)
from app.models import Student, Cohort

instructor = Blueprint('instructor', __name__)


@instructor.route('/')
@login_required
def index():
    """Instructor dashboard page."""
    return render_template('instructor/index.html')


@instructor.route('/cohorts')
@login_required
def registered_cohorts():
    """View all registered users."""
    cohorts = Cohort.query.all()
    return render_template(
        'instructor/registered_cohorts.html', cohorts=cohorts)


@instructor.route('/new-cohort', methods=['GET', 'POST'])
@login_required
def new_cohort():
    """Create a new cohort."""
    form = NewCohortForm()
    if form.validate_on_submit():
        cohort = Cohort(
            name=form.cohort_name.data,
            slug=form.cohort_slug.data,
            start_date=form.start_date.data,
            graduation_date=form.graduation_date.data)
        db.session.add(cohort)
        db.session.commit()
        flash('Cohort {} successfully created'.format(cohort.name),
              'form-success')
    return render_template('instructor/new_cohort.html', form=form)

@instructor.route('/students')
@login_required
def registered_students():
    """View all registered users."""
    students = Student.query.all()
    students.sort(key=lambda s: (s.cohort and s.cohort.name) or ' ',
                  reverse=True)
    cohorts = Cohort.query.all()
    return render_template(
        'instructor/registered_students.html', students=students, cohorts=cohorts)


@instructor.route('/new-student', methods=['GET', 'POST'])
@login_required
def new_student():
    """Upload a list of students."""
    form = NewStudentForm()
    if form.validate_on_submit():
        if form.roster.data:
            roster_data = form.roster.data.read().decode('utf-8')
            first_line = roster_data.split('\n')[0]
            required_keys = ['first_name',
                             'last_name',
                             'email']
            if all(x in first_line for x in required_keys):
                session['rostercsv'] = roster_data
                return redirect(url_for('.show_uploaded_students'))
            msg = Markup('Missing fields in form. CSV header requires "first_name", "last_name", and "email"'
                         '<br>Fields received: <ul><li>{}</li></ul>'.format('</li><br><li>'.join(first_line.split(','))))
            flash(msg, 'form-error')
        elif form.first_name.data:
            student = Student(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                cohort=form.cohort.data)
            db.session.add(student)
            db.session.commit()
            msg = Markup(f'Student <b>{form.first_name.data} {form.last_name.data}</b> successfully created')
            flash(msg, 'form-success')
    return render_template('instructor/new_student.html', form=form)


@instructor.route('/upload-students', methods=['GET', 'POST'])
@login_required
def show_uploaded_students():
    """Upload a list of students."""
    form = StudentUploadForm()
    roster = session.get('rostercsv', '')
    reader = csv.DictReader(StringIO(roster))
    students = []
    for row in reader:
        student = Student(
            first_name=row['first_name'],
            last_name=row['last_name'],
            email=row['email'])
        student.valid = bool(Student.query.filter_by(email=row['email']).first())
        students.append(student)

    if form.validate_on_submit():
        # TODO: remove unselected students
        for s in students:
            s.cohort = form.cohort.data
        db.session.bulk_save_objects(students)
        db.session.commit()
        flash('{} students successfully created'.format(len(students)),
              'form-success')
        # return redirect(url_for('.registered_students'))
    return render_template('instructor/upload_students.html', form=form, students=students)


@instructor.route('/student/<int:student_id>')
@instructor.route('/student/<int:student_id>/info')
@login_required
def student_info(student_id):
    """View a user's profile."""
    student = Student.query.filter_by(id=student_id).first()
    if student is None:
        abort(404)
    return render_template('instructor/manage_student.html', student=student)


@instructor.route('/student/<int:student_id>/change-email', methods=['GET', 'POST'])
@login_required
def change_student_email(student_id):
    """Change a student's email."""
    student = Student.query.filter_by(id=student_id).first()
    if student is None:
        abort(404)
    form = ChangeStudentEmailForm()
    if form.validate_on_submit():
        student.email = form.email.data
        db.session.add(student)
        db.session.commit()
        flash('Email for student {} successfully changed to {}.'.format(
            student.full_name(), student.email), 'form-success')
    return render_template('instructor/manage_student.html', student=student, form=form)


@instructor.route('/student/<int:student_id>/change-cohort', methods=['GET', 'POST'])
@login_required
def change_student_cohort(student_id):
    """Change a student's email."""
    student = Student.query.filter_by(id=student_id).first()
    if student is None:
        abort(404)
    form = ChangeStudentCohortForm()
    if form.validate_on_submit():
        student.cohort = form.cohort.data
        db.session.add(student)
        db.session.commit()
        flash('{} successfully moved to cohort {}.'.format(
            student.full_name(), student.cohort.name), 'success')
        return redirect(url_for('.student_info', student_id=student_id))
    return render_template('instructor/manage_student.html', student=student, form=form)


@instructor.route('/student/<int:student_id>/delete')
@login_required
def delete_student_request(student_id):
    """Request deletion of a student."""
    student = Student.query.filter_by(id=student_id).first()
    if student is None:
        abort(404)
    return render_template('instructor/manage_student.html', student=student)


@instructor.route('/student/<int:student_id>/_delete')
@login_required
def delete_student(student_id):
    """Delete a student."""
    student = Student.query.filter_by(id=student_id).first()
    db.session.delete(student)
    db.session.commit()
    flash('Successfully deleted student %s.' % student.full_name(), 'success')
    return redirect(url_for('.registered_students'))
