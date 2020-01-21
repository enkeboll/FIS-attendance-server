from flask import (
    Blueprint,
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
    cohorts = Cohort.query.all()
    # current_app.logger.info(students)
    # current_app.logger.info(cohorts)
    return render_template(
        'instructor/registered_students.html', students=students, cohorts=cohorts)


@instructor.route('/new-student', methods=['GET', 'POST'])
@login_required
def new_student():
    """Upload a list of students."""
    form = NewStudentForm()
    if form.validate_on_submit():
        if form.roster.data:
            session['rostercsv'] = form.roster.data.read().decode('utf-8').split('\n')
            return redirect(url_for('.show_uploaded_students'))
        student = Student(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            cohort=form.cohort.data)
        db.session.add(student)
        db.session.commit()
        flash('Student {} {} successfully created'.format(form.first_name,
                                                          form.last_name),
              'form-success')
    return render_template('instructor/new_student.html', form=form)


@instructor.route('/upload-students', methods=['GET', 'POST'])
@login_required
def show_uploaded_students():
    """Upload a list of students."""
    roster = session.get('rostercsv', [])
    form = StudentUploadForm()
    return render_template('instructor/upload_students.html', form=form, data=roster)


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
    return redirect(url_for('instructor.registered_students'))
