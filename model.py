from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class MMUBuilding(db.Model):
    __tablename__ = 'mmu_buildings'

    buildings_id = db.Column(db.Integer, primary_key=True, nullable=False)
    building_name = db.Column(db.String(60), unique=True, nullable=False)
    description = db.Column(db.String(255))
    location_coord = db.Column(db.String(100))

    rooms = db.relationship('Room', backref='building', lazy=True)
    events = db.relationship('Event', backref='building', lazy=True)

class Room(db.Model):
    __tablename__ = 'rooms'

    room_id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(60), nullable=False)
    room_type = db.Column(db.String(45), nullable=False)
    building_id = db.Column(db.Integer, db.ForeignKey('mmu_buildings.buildings_id'), nullable=False)

    events = db.relationship('Event', backref='room', lazy=True)

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    event_time = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    building_id = db.Column(db.Integer, db.ForeignKey('mmu_buildings.buildings_id'), nullable=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.room_id'), nullable=True)