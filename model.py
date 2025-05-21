from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

db = SQLAlchemy()

event_participants = db.Table('event_participants',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('events.id'))
)

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)

    joined_events = db.relationship('Event', secondary=event_participants, backref='participants')


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class MMUBuilding(db.Model):
    __tablename__ = 'mmu_buildings'
    id = db.Column(db.Integer, primary_key=True)
    building_name = db.Column(db.String(100), nullable=False)
    rooms = db.relationship('Room', backref='building', lazy=True)
    events = db.relationship('Event', backref='building_info', lazy=True)


class Room(db.Model):
    __tablename__ = 'rooms'
    room_id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(100), nullable=False)
    building_id = db.Column(db.Integer, db.ForeignKey('mmu_buildings.id'), nullable=False)
    events = db.relationship('Event', backref='room_info', lazy=True)


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    event_type = db.Column(db.String(100), nullable=False)
    venue_code = db.Column(db.Integer, nullable=True)  # Not used anymore, optional
    organizer = db.Column(db.String(100), nullable=False)
    event_time = db.Column(db.DateTime, nullable=False)
    maximum_capacity = db.Column(db.Integer, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    cancelled = db.Column(db.Boolean, default=False)


    building_id = db.Column(db.Integer, db.ForeignKey('mmu_buildings.id'), nullable=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.room_id'), nullable=True)

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notify_at = db.Column(db.DateTime, nullable=False)  # When the notification should be triggered

    user = db.relationship('User', backref='notifications', lazy=True)

class Comment(db.Model):
    __tablename__ = 'comments'

    comment_id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)

    user = db.relationship('User', backref='comments')
    event = db.relationship('Event', backref='comments')