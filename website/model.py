from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    _tablename_ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class MMUBuilding(db.Model):
    _tablename_ = 'mmu_buildings'
    id = db.Column(db.Integer, primary_key=True)
    building_name = db.Column(db.String(100), nullable=False)
    rooms = db.relationship('Room', backref='building', lazy=True)
    events = db.relationship('Event', backref='building_info', lazy=True)


class Room(db.Model):
    _tablename_ = 'rooms'
    room_id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(100), nullable=False)
    building_id = db.Column(db.Integer, db.ForeignKey('mmu_buildings.id'), nullable=False)
    events = db.relationship('Event', backref='room_info', lazy=True)


class Event(db.Model):
    _tablename_ = 'events'
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

    class Booking(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        room_id = db.Column(db.String(50), nullable=False)
        pax = db.Column(db.Integer, nullable=False)
        date = db.Column(db.String(20), nullable=False)
        time = db.Column(db.String(20), nullable=False)
        

    building_id = db.Column(db.Integer, db.ForeignKey('mmu_buildings.id'), nullable=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.room_id'), nullable=True)