from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from model import db, MMUBuilding, Room, User, Event
from flask_migrate import Migrate
from datetime import datetime
import os

# Initialize Flask app
app = Flask(__name__,
    instance_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance'),
    instance_relative_config=True)

# Direct configuration in app.py (without .env file)
app.config['SECRET_KEY'] = 'f8695bd59f8d4121b877d34ae6efeb3d'  # Directly set the SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Directly set the DATABASE URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable SQLAlchemy modification tracking

# Initialize the database
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter((User.username == username) | (User.email == email)).first():
            return redirect(url_for('signup'))

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('userpage'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('userpage'))
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/userpage')
@login_required
def userpage():
    my_events = Event.query.filter_by(created_by=current_user.id).all()
    return render_template('userpage.html', my_events=my_events)

@app.route("/join", methods=['GET', 'POST'])
@login_required
def join():
    search_query = request.args.get('search', '').lower()
    if search_query:
        other_events = Event.query.filter(
            Event.created_by != current_user.id,
            db.or_(
                Event.name.ilike(f'%{search_query}%'),
                Event.event_type.ilike(f'%{search_query}%'),
                Event.organizer.ilike(f'%{search_query}%')
            )
        ).all()
    else:
        other_events = Event.query.filter(Event.created_by != current_user.id).all()

    return render_template("join.html", other_events=other_events)

@app.route('/comment')
@login_required
def comment():
    return render_template('comment.html')

@app.route('/create', methods=['GET'])
@login_required
def create_event():
    buildings = MMUBuilding.query.all()
    rooms = Room.query.all()
    return render_template('create.html', buildings=buildings, rooms=rooms)

@app.route('/create', methods=['POST'])
@login_required
def create_event_post():
    try:
        event_name = request.form['event_name']
        event_type = request.form['event_type']
        organizer = request.form['organizer']
        date = request.form['date']
        time_str = request.form['time']
        event_datetime = datetime.strptime(f"{date} {time_str}", "%Y-%m-%d %H:%M")
        maximum_capacity = int(request.form['maximum_capacity'])
        created_by = int(request.form['created_by'])
        building_id = request.form['building_id'] or None
        room_id = request.form['room_id'] or None

        new_event = Event(
            name=event_name,
            event_type=event_type,
            venue_code=None,
            organizer=organizer,
            event_time=event_datetime,
            maximum_capacity=maximum_capacity,
            created_by=created_by,
            building_id=building_id,
            room_id=room_id
        )
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('userpage'))
    except Exception as e:
        return f"Error: {e}", 400
    
@app.route('/cancel_event', methods=['POST'])
@login_required
def cancel_event():
    event = Event.query.get_or_404()

    if event.created_by != current_user.id:
        flash("You are not authorised to delete this event.", "danger")
        return redirect(url_for('/userpage'))

    event.cancelled = True
    db.session.commit()
    flash('Event successfully cancelled!', 'info')
    return redirect(url_for('/userpage'))
    Event.query.filter_by(cancelled=False).all()

@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    user = User.query.get(current_user.id)
    Event.query.filter_by(created_by=user.id).delete()

    db.session.delete(user)
    db.session.commit()

    logout_user()
    flash("Account successfully deleted!", "info")
    return redirect(url_for('/login'))

if __name__ == '__main__':
    app.run(debug=True)