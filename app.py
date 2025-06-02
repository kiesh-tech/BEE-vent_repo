from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from model import db, MMUBuilding, Room, User, Event, event_participants, Notification, Comment
from flask_migrate import Migrate
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
from datetime import datetime, timedelta
import os
import random

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

def to_malaysia_time(dt_utc):
    if dt_utc is None:
        return None
    utc = pytz.utc
    malaysia_tz = pytz.timezone('Asia/Kuala_Lumpur')

    # Make sure the datetime is timezone-aware UTC
    if dt_utc.tzinfo is None:
        dt_utc = utc.localize(dt_utc)
    else:
        dt_utc = dt_utc.astimezone(utc)

    # Convert to Malaysia time
    return dt_utc.astimezone(malaysia_tz)

def send_upcoming_event_notifications(user):
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    one_day = now + timedelta(days=1)
    two_hours = now + timedelta(hours=2)

    joined_events = Event.query.join(event_participants).filter(
        event_participants.c.user_id == user.id
    ).all()

    notifications = []

    for event in joined_events:
        time_until_event = event.event_time - now

        existing = Notification.query.filter_by(user_id=user.id, id=event.id).all()
        if existing:
            continue

        if timedelta(hours=1.5) < time_until_event <= timedelta(hours=2.5):
           msg = f"Reminder: '{event.name}' starts in 2 hours!"
        elif timedelta(hours=23) < time_until_event <= timedelta(hours=25):
           msg = f"Reminder: '{event.name}' is tomorrow!"
        else:
            continue

        note = Notification(user_id=user.id, content=msg, notify_at=now)
        db.session.add(note)
        notifications.append(note)

    db.session.commit()
    return notifications

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
        
        login_user(new_user)
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
    send_upcoming_event_notifications(current_user)

    my_events = Event.query.filter_by(created_by=current_user.id).all()
    joined_events = Event.query.join(event_participants).filter(
        event_participants.c.user_id == current_user.id
    ).all()
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(
        Notification.notify_at.desc()
    ).all()
    unread_notifications_count = len(notifications)

    # Mark notifications as read
    for notification in notifications:
        notification.read = True
    db.session.commit()

    return render_template(
        'userpage.html',
        my_events=my_events,
        joined_events=joined_events,
        notifications=notifications, unread_notifications_count=unread_notifications_count
    )

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

@app.route('/join_event/<int:event_id>', methods=['POST'])
@login_required
def join_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Check if the user is already a participant
    if current_user not in event.participants:
        event.participants.append(current_user)
        db.session.commit()

        # Add a notification for the user who joined the event
        # Notify 1 day before the event starts
        notify_at = event.event_time - timedelta(days=1)

        # Create the notification content
        notification_content = f"🔔 Reminder: Your event '{event.name}' is starting soon in 1 day!"

        notification = Notification(
            content=notification_content,
            user_id=current_user.id,
            notify_at=notify_at
        )
        db.session.add(notification)
        db.session.commit()

        flash("Successfully joined the event!", "success")

    return redirect(url_for('userpage'))

@app.route('/mark_notifications_read', methods=['POST'])
@login_required
def mark_notifications_read():
    notifications = Notification.query.filter_by(user_id=current_user.id, read=False).all()
    for notification in notifications:
        notification.read = True
    db.session.commit()

    return redirect(url_for('userpage'))

@app.route('/event/<int:event_id>/comment', methods=['GET', 'POST'])
@login_required
def event_comment(event_id):
    event = Event.query.get_or_404(event_id)

    if request.method == 'POST':
        content = request.form['content']
        comment = Comment(content=content, user_id=current_user.id, event_id=event_id)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('event_comment', event_id=event_id))

    comments = Comment.query.filter_by(event_id=event_id).order_by(Comment.timestamp.desc()).all()
    
    for comment in comments:
        comment.local_timestamp = to_malaysia_time(comment.timestamp)
    
    return render_template('comment.html', event=event, comments=comments)

if __name__ == '__main__':
    app.run(debug=True)