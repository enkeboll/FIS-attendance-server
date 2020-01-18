from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import (
    PasswordField,
    StringField,
    SubmitField,
)
from wtforms.fields.html5 import DateField, EmailField
from wtforms.validators import (
    Email,
    EqualTo,
    InputRequired,
    Length,
)

from app import db
from app.models import Student


class ChangeStudentEmailForm(FlaskForm):
    email = EmailField(
        'New email', validators=[InputRequired(),
                                 Length(1, 64),
                                 Email()])
    submit = SubmitField('Update email')

    def validate_email(self, field):
        if Student.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

class NewCohortForm(FlaskForm):
    # TODO: coach selector
    # role = QuerySelectField(
    #     'Account type',
    #     validators=[InputRequired()],
    #     get_label='name',
    #     query_factory=lambda: db.session.query(Role).order_by('permissions'))

    cohort_slug = StringField(
        'Cohort slug', validators=[InputRequired(),
                                   Length(1, 64)])
    cohort_name = StringField(
        'Cohort name', validators=[InputRequired(),
                                   Length(1, 64)])

    start_date = DateField(
        'Start Date',
        format='%Y-%m-%d',
        validators=[InputRequired()])
    
    graduation_date = DateField(
        'Graduation Date',
        format='%Y-%m-%d',
        validators=[InputRequired()])

    submit = SubmitField('Create')

    def validate_slug(self, field):
        if Cohort.query.filter_by(slug=field.data).first():
            raise ValidationError('Cohort slug already registered.')


class NewStudentForm(FlaskForm):

    first_name = StringField(
        'First Name', validators=[InputRequired(),
                                  Length(1, 64)])
    last_name = StringField(
        'Last Name', validators=[InputRequired(),
                                 Length(1, 64)])

    email = EmailField(
        'Email Address', validators=[InputRequired(),
                                     Length(1, 64),
                                     Email()])
    
    idcard_id = StringField(
        'ID Card ID', validators=[InputRequired()])

    cohort_id = StringField(
        'Cohort ID', validators=[InputRequired()])

    submit = SubmitField('Create')

    def validate_email(self, field):
        if Student.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

