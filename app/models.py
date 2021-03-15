from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db, login





partecipation = db.Table('partecipation',
                   db.Column('student_id', db.Integer, db.ForeignKey('student.id')),
                   db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
                )

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('student.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('student.id'))
)

class Student(UserMixin, db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password=db.Column(db.String(100),nullable=False)
    university = db.Column(db.String(50), nullable=True)
    image_file = db.Column(db.String(50), nullable=False, default='default.jpg')
    about_me = db.Column(db.String(140))
    partecipations = db.relationship('Event', secondary=partecipation, backref=db.backref('partecipants', lazy='joined'))
    followed = db.relationship(
        'Student', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    
    def __repr__(self):
        return "<Student %r>" % self.name
    
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

@login.user_loader
def load_user(id):
    return Student.query.get(int(id))

class Event(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=True)
    date = db.Column(db.Date)
    bp_id = db.Column(db.Integer, db.ForeignKey('businesspartner.id'))
    description=db.Column(db.String(500))
    numofPeople = db.Column(db.Integer)
    location = db.Column(db.String(100))
    #partecipants = db.relationship("Student", secondary=partecipation)

    def __repr__(self):
        return "<Event %r>" % self.name


class BusinessPartner(db.Model):
    __tablename__ = 'businesspartner'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    events = db.relationship('Event', backref='creator', ) #creator column of the Event row contains the BP who created it

    def __repr__(self):
        return "<Business Partner %r>" % self.name
