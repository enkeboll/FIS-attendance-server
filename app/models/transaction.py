from .. import db


class IDCard(db.Model):
    __tablename__ = 'id_card'
    id = db.Column(db.Integer, primary_key=True)
    serial_no = db.Column(db.String(64), index=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())

    students = db.relationship('Student', backref='id_card', lazy='dynamic')

    def __repr__(self):
        return f'<IDCard {self.serial_no}>'



class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(64))
    idcard_id = db.Column(db.Integer, db.ForeignKey('id_card.id'))
    cohort_id = db.Column(db.Integer, db.ForeignKey('cohort.id'))
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())

    def __init__(self, **kwargs):
        super(Student, self).__init__(**kwargs)
        # if self.cohort is None:
        self.cohort = Cohort.query.filter_by(id=self.cohort_id)
        # if self.idcard is None:
        self.idcard = IDCard.query.filter_by(id=self.idcard_id)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __repr__(self):
        return f'<Student {self.first_name} {self.last_name}'


class PunchIn(db.Model):
    __tablename__ = 'punch_in'
    id = db.Column(db.Integer, primary_key=True)
    idcard_id = db.Column(db.Integer, db.ForeignKey('id_card.id'))
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), index=True)

    def __repr__(self):
        return f'<PunchIn {self.idcard_id} @ {self.created_at}>'

class Cohort(db.Model):
    __tablename__ = 'cohort'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())

    def __repr__(self):
        return f'<Cohort {self.name}>'
