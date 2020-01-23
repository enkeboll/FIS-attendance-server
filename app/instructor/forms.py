from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed

from werkzeug import secure_filename

from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import (
    SelectField,
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
from app.models import Student, Cohort
from app.utils import RequiredIfNot


class ChangeStudentEmailForm(FlaskForm):
    email = EmailField(
        'New email', validators=[InputRequired(),
                                 Length(1, 64),
                                 Email()])
    submit = SubmitField('Update email')

    def validate_email(self, field):
        if Student.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class ChangeStudentCohortForm(FlaskForm):
    cohort = QuerySelectField(
        'Cohort Name',
        validators=[],
        get_label='name',
        query_factory=lambda: db.session.query(Cohort).order_by(Cohort.start_date.desc()))

    submit = SubmitField('Update Cohort')


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
            raise ValidationError('Cohort already created.')


class NewStudentForm(FlaskForm):

    roster = FileField(
        "Upload Roster for Single Cohort. Format expected is the output from "
        "<a href='https://learn.co/batches'>https://learn.co/batches</a>",
        validators=[FileAllowed(['csv'])])

    first_name = StringField(
        'First Name', validators=[RequiredIfNot('roster'),
                                  Length(1, 64)])
    last_name = StringField(
        'Last Name', validators=[RequiredIfNot('roster'),
                                 Length(1, 64)])

    email = EmailField(
        'Email Address', validators=[RequiredIfNot('roster'),
                                     Length(1, 64),
                                     Email()])

    cohort = QuerySelectField(
        'Cohort Name (optional)',
        validators=[],
        get_label='name',
        query_factory=lambda: db.session.query(Cohort).order_by(Cohort.start_date.desc()),
        allow_blank=True, blank_text='No Cohort')

    submit_button = SubmitField('Create')

    def validate_email(self, field):
        if Student.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class StudentUploadForm(FlaskForm):

    cohort = QuerySelectField(
        'Cohort Name',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(Cohort).order_by(Cohort.start_date.desc()))

    submit = SubmitField('Create')

