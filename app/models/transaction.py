from .. import db


class IDCard(db.Model):
    __tablename__ = 'id_card'
    id = db.Column(db.Integer, primary_key=True)
    serial_no = db.Column(db.String(64), index=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())

    students = db.relationship('Student', backref='idcard', lazy=True)

    @staticmethod
    def generate_fake(count=100, **kwargs):
        """Generate a number of fake users for testing."""
        from sqlalchemy.exc import IntegrityError
        from random import seed, randint
        from faker import Faker

        fake = Faker()

        seed()
        for i in range(count):
            idc = IDCard(
                serial_no=randint(1000, 9999),
                **kwargs)
            db.session.add(idc)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

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

    # Backrefs
    # cohort
    # idcard

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @staticmethod
    def generate_fake(count=100, **kwargs):
        """Generate a number of fake users for testing."""
        from sqlalchemy.exc import IntegrityError
        from random import seed, choice
        from faker import Faker

        fake = Faker()
        cohorts = Cohort.query.all()

        seed()
        for i in range(count):
            s = Student(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                cohort_id=choice(cohorts).id,
                **kwargs)
            db.session.add(s)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

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
    slug = db.Column(db.String(64))
    start_date = db.Column(db.Date())
    graduation_date = db.Column(db.Date(), default=start_date + 102)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())

    students = db.relationship('Student', backref='cohort', lazy=True)

    @staticmethod
    def generate_fake(count=100, **kwargs):
        """Generate a number of fake users for testing."""
        from sqlalchemy.exc import IntegrityError
        from random import seed, randint, choice
        from faker import Faker
        from datetime import date, timedelta

        fake = Faker()
        disciplines = ('DS', 'SE', 'CS', 'UX')

        seed()
        for i in range(count):
            start_date = date.today() - timedelta(randint(0, 90))
            disc = choice(disciplines)
            name = f"DC {disc} {start_date.strftime('%m%d%y')}"
            c = Cohort(
                name=name,
                slug=name.replace(' ', '-'),
                start_date=start_date,
                graduation_date=start_date + timedelta(102),
                **kwargs)
            db.session.add(c)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


    def __repr__(self):
        return f'<Cohort {self.name}>'
