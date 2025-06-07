from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from model import db, MMUBuilding, Room, User, Event, event_participants, Notification, Comment
from flask_migrate import Migrate
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
from datetime import datetime, timedelta
import os
import random
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3

# Enable foreign key enforcement for SQLite
@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):  # For SQLite only
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

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
    now_utc = datetime.utcnow()
    now = to_malaysia_time(now_utc)

    joined_events = Event.query.join(event_participants).filter(
        event_participants.c.user_id == user.id
    ).all()

    for event in joined_events:
        event_time = to_malaysia_time(event.event_time)
        time_until_event = event_time - now

        if time_until_event.total_seconds() < 0:
            continue

        notifications_to_send = []

        # Send "tomorrow" reminder if event is between 23h and 48h away
        if timedelta(hours=23) < time_until_event <= timedelta(hours=48):
            msg = f"📅 Reminder: '{event.name}' is coming up tomorrow!"
            notifications_to_send.append(msg)

        # Send "2 hours before" reminder if event is between 1h and 2h away
        if timedelta(hours=1) < time_until_event <= timedelta(hours=2):
            msg = f"🔔 Reminder: '{event.name}' starts in 2 hours!"
            notifications_to_send.append(msg)

        for msg in notifications_to_send:
            existing = Notification.query.filter_by(
                user_id=user.id, event_id=event.id, content=msg
            ).first()

            if not existing:
                note = Notification(
                    user_id=user.id,
                    content=msg,
                    event_id=event.id,
                    notify_at=now_utc
                )
                db.session.add(note)

    db.session.commit()

def generate_gradient():
    import random
    colors = [
        "#FFB6C1", "#87CEEB", "#90EE90", "#FFD700",
        "#FFA07A", "#9370DB", "#00CED1", "#FF69B4",
        "#00FA9A", "#FF6347", "#6A5ACD", "#40E0D0",
        "#FF8C00", "#BA55D3", "#7B68EE", "#20B2AA",
        "#F08080", "#00BFFF", "#D8BFD8", "#B0E0E6"
    ]

    shapes = [
        "linear-gradient(135deg, {0}, {1})",
        "linear-gradient(45deg, {0}, {1})",
        "linear-gradient(to right, {0}, {1})",
        "radial-gradient(circle, {0}, {1})",
        "radial-gradient(ellipse at center, {0}, {1})",
        "repeating-linear-gradient(45deg, {0}, {0} 10px, {1} 10px, {1} 20px)",
        "repeating-linear-gradient(-45deg, {0}, {0} 15px, {1} 15px, {1} 30px)",
        "repeating-radial-gradient(circle, {0}, {0} 10px, {1} 10px, {1} 20px)",
        "repeating-radial-gradient(ellipse, {0}, {0} 15px, {1} 15px, {1} 30px)",
        "conic-gradient(from 90deg at 50% 50%, {0}, {1})"
    ]

    c1, c2 = random.sample(colors, 2)
    pattern = random.choice(shapes)
    return pattern.format(c1, c2)

    

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
    return redirect(url_for('home'))

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
        notification.local_notify_at = to_malaysia_time(notification.notify_at)
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

@app.route('/comment/<int:event_id>', methods=['GET'])
@login_required
def comment(event_id):
    event = Event.query.get_or_404(event_id)
    comments = Comment.query.filter_by(event_id=event_id).order_by(Comment.timestamp.desc()).all()

    for comment in comments:
        comment.local_timestamp = to_malaysia_time(comment.timestamp)

    return render_template('comment.html', event=event, comments=comments)

@app.route('/create', methods=['GET'])
@login_required
def create_event():
    buildings = MMUBuilding.query.all()
    rooms = Room.query.all()

    selected_building = request.args.get('building', '').lower()
    selected_room = request.args.get('room', '').lower()
    return render_template('create.html', buildings=buildings, rooms=rooms, selected_building=selected_building, selected_room=selected_room)

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

        start_window = event_datetime - timedelta(hours=2)
        end_window = event_datetime + timedelta(hours=2)

        conflict_query = Event.query.filter(
            Event.cancelled != True,
            Event.event_time >= start_window,
            Event.event_time <= end_window
        )

        if building_id:
            conflict_query = conflict_query.filter(Event.building_id == building_id)
        if room_id:
            conflict_query = conflict_query.filter(Event.room_id == room_id)

        conflict_event = conflict_query.first()
        if conflict_event:
            flash("❌ Building or room is already booked within 2 hours of the selected time. Please choose another time.", "danger")
            return redirect(url_for('userpage'))


        new_event = Event(
            name=event_name,
            event_type=event_type,
            venue_code=None,
            organizer=organizer,
            event_time=event_datetime,
            maximum_capacity=maximum_capacity,
            created_by=created_by,
            building_id=building_id,
            room_id=room_id,
            bg_gradient=generate_gradient()
        )
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('userpage'))
    except Exception as e:
        return f"Error: {e}", 400
    
@app.route('/delete_event/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)

    Comment.query.filter_by(event_id=event.id).delete()

    if event.created_by == current_user.id:
        Notification.query.filter_by(event_id=event.id).delete()
        db.session.delete(event)
        db.session.commit()
        flash("✅ Event deleted.", "success")
    elif current_user in event.participants:
        event.participants.remove(current_user)  # Assuming many-to-many relationship
        Notification.query.filter_by(user_id=current_user.id, event_id=event.id).delete()
        db.session.commit()
        flash("🚪 You have left the event.", "info")
    else:
        flash("❌ Not authorized to delete or leave this event.", "danger")

    return redirect(url_for('userpage'))

from flask_login import current_user, logout_user
from flask import flash, redirect, url_for

@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    user = current_user

    Comment.query.filter_by(user_id=current_user.id).delete()

    # Cancel events created by the user
    for event in user.created_events:
        event.cancelled = True

    # Remove user from events they joined (optional but good practice)
    for event in user.joined_events:
        event.participants.remove(user)

    db.session.delete(user)
    db.session.commit()

    logout_user()
    return redirect(url_for('home'))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
     if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if not current_user.check_password(current_password):
            flash("❌ Current password is incorrect.", "danger")
        elif new_password != confirm_password:
            flash("❌ New passwords do not match.", "danger")
        else:
            current_user.set_password(new_password)
            db.session.commit()
            flash("✅ Password updated successfully.", "success")
            return redirect(url_for('userpage'))

     return render_template('change_password.html')

@app.route('/join_event/<int:event_id>', methods=['POST'])
@login_required
def join_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    if current_user not in event.participants:
        event.participants.append(current_user)
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

@app.route('/mmu_map')
def mmu_map():
    return render_template('mmu_map.html')

@app.route('/building')
def building_select():
    return render_template('map_building.html')

@app.route('/building/<building_name>')
def building_page(building_name):
    building_name = building_name.lower()
    if building_name in ['fci', 'fcm', 'fom', 'clc']:
        return render_template(f'{building_name}.html')  # SVG maps
    else:
        return redirect(url_for('create_event', building=building_name))

@app.route('/select_room', methods=['POST'])
def select_room():
    building = request.form.get('building')
    room = request.form.get('room')
    return redirect(url_for('create_event', building=building, room=room))

if __name__ == '__main__':
    app.run(debug=True)