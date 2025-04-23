from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class MMUBuilding(db.Model):
    __tablename__ = 'mmu_buildings'

    buildings_id = db.Column(db.Integer, primary_key=True, nullable=False)
    building_name = db.Column(db.String(60), unique=True, nullable=False)
    description = db.Column(db.String(255))
    location_coord = db.Column(db.String(100))

    rooms = db.relationship('Room', backref='building', lazy=True)

class Room(db.Model):
    __tablename__ = 'rooms'

    room_id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(60), nullable=False)
    room_type = db.Column(db.String(45), nullable=False)
    building_id = db.Column(db.Integer, db.ForeignKey('mmu_buildings.buildings_id'), nullable=False)


