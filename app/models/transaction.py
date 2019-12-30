from .. import db


class IDCard(db.Model):
    __tablename__ = 'id_card'
    id = db.Column(db.Integer, primary_key=True)
    serial_no = db.Column(db.String(10), index=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())

    students = db.relationship('Student', backref='id_card', lazy='dynamic')


class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(64))
    idcard_id = db.Column(db.Integer, db.ForeignKey('idcard.id'))
    cohort_id = db.Column(db.Integer, db.ForeignKey('cohort.id'))
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())


class PunchIn(db.Model):
    __tablename__ = 'punch_in'
    id = db.Column(db.Integer, primary_key=True)
    idcard_id = db.Column(db.Integer, db.ForeignKey('idcard.id'))
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), index=True)
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())


class Cohort(db.Model):
    __tablename__ = 'cohort'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())
