from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from .model import db, MMUBuilding, Room, User, Event
from datetime import datetime

def create_app():
    app = Flask(__name__)
    app.secret_key = 'beeevents3'

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Hr060491#@localhost/sql_bee_events'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Initialize DB
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Flask-Login setup
    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    app.register_blueprint(views)

    with app.app_context():
        db.create_all()

    return app
