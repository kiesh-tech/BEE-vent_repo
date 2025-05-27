from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

# Association Table for Many-to-Many: User <-> Event
event_participants = db.Table(
    'event_participants',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), primary_key=True)
)

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)

    created_events = db.relationship('Event', back_populates='creator', cascade='all, delete-orphan', passive_deletes=True)
    joined_events = db.relationship('Event', secondary=event_participants, back_populates='participants')
    notifications = db.relationship('Notification', back_populates='user', cascade='all, delete-orphan', passive_deletes=True)
    comments = db.relationship('Comment', back_populates='user', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class MMUBuilding(db.Model):
    __tablename__ = 'mmu_buildings'

    id = db.Column(db.Integer, primary_key=True)
    building_name = db.Column(db.String(100), nullable=False)

    rooms = db.relationship('Room', back_populates='building', cascade='all, delete-orphan', passive_deletes=True)
    events = db.relationship('Event', back_populates='building_info', cascade='all, delete-orphan', passive_deletes=True)


class Room(db.Model):
    __tablename__ = 'rooms'

    room_id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(100), nullable=False)
    building_id = db.Column(db.Integer, db.ForeignKey('mmu_buildings.id', ondelete='CASCADE'), nullable=False)

    building = db.relationship('MMUBuilding', back_populates='rooms')
    events = db.relationship('Event', back_populates='room_info', cascade='all, delete-orphan', passive_deletes=True)
    


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    event_type = db.Column(db.String(100), nullable=False)
    organizer = db.Column(db.String(100), nullable=False)
    event_time = db.Column(db.DateTime, nullable=False)
    maximum_capacity = db.Column(db.Integer, nullable=False)
    venue_code = db.Column(db.Integer, nullable=True)
    cancelled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bg_gradient = db.Column(db.String(200))

    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    building_id = db.Column(db.Integer, db.ForeignKey('mmu_buildings.id', ondelete='SET NULL'), nullable=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.room_id', ondelete='SET NULL'), nullable=True)

    creator = db.relationship('User', back_populates='created_events')
    building_info = db.relationship('MMUBuilding', back_populates='events')
    room_info = db.relationship('Room', back_populates='events')
    participants = db.relationship('User', secondary=event_participants, back_populates='joined_events')
    notifications = db.relationship('Notification', back_populates='event', cascade='all, delete-orphan', passive_deletes=True)
    comments = db.relationship('Comment', back_populates='event', cascade='all, delete-orphan', passive_deletes=True)

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notify_at = db.Column(db.DateTime, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=True)

    user = db.relationship('User', back_populates='notifications')
    event = db.relationship('Event', back_populates='notifications')

class Comment(db.Model):
    __tablename__ = 'comments'

    comment_id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False)

    user = db.relationship('User', back_populates='comments')
    event = db.relationship('Event', back_populates='comments')