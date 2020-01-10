from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    current_app
)
from flask_login import current_user, login_required
from flask_rq import get_queue

from app import db
from app.instructor.forms import ChangeStudentEmailForm
from app.models import Student, Cohort

instructor = Blueprint('instructor', __name__)


@instructor.route('/')
@login_required
def index():
    """Admin dashboard page."""
    return render_template('instructor/index.html')


# @instructor.route('/new-user', methods=['GET', 'POST'])
# @login_required
# def new_user():
#     """Create a new user."""
#     form = NewUserForm()
#     if form.validate_on_submit():
#         user = User(
#             role=form.role.data,
#             first_name=form.first_name.data,
#             last_name=form.last_name.data,
#             email=form.email.data,
#             password=form.password.data)
#         db.session.add(user)
#         db.session.commit()
#         flash('User {} successfully created'.format(user.full_name()),
#               'form-success')
#     return render_template('instructor/new_user.html', form=form)


@instructor.route('/students')
@login_required
def registered_students():
    """View all registered users."""
    students = Student.query.all()
    cohorts = Cohort.query.all()
    current_app.logger.info(students)
    current_app.logger.info(cohorts)
    return render_template(
        'instructor/registered_students.html', students=students, cohorts=cohorts)


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


# @instructor.route(
#     '/user/<int:user_id>/change-account-type', methods=['GET', 'POST'])
# @login_required
# def change_account_type(user_id):
#     """Change a user's account type."""
#     if current_user.id == user_id:
#         flash('You cannot change the type of your own account. Please ask '
#               'another administrator to do this.', 'error')
#         return redirect(url_for('admin.user_info', user_id=user_id))

#     user = User.query.get(user_id)
#     if user is None:
#         abort(404)
#     form = ChangeAccountTypeForm()
#     if form.validate_on_submit():
#         user.role = form.role.data
#         db.session.add(user)
#         db.session.commit()
#         flash('Role for user {} successfully changed to {}.'.format(
#             user.full_name(), user.role.name), 'form-success')
#     return render_template('instructor/manage_user.html', user=user, form=form)


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
    return redirect(url_for('admin.registered_students'))
