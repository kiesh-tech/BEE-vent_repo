from flask import Blueprint, render_template
from flask_login import current_user
from flask_login import login_required, current_user


views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user)

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
    return render_template('userpage.html')

@app.route('/join')
@login_required
def join():
    return render_template('join.html')

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

@app.route('/map')
def map_view():
    room_status = {
        "cnmx1001": "available",
        "cnmx1002": "available",
        "cnmx1003": "available",
        "cnmx1004": "available",
        "cnmx1005": "available",
        "cnmx1006": "available",
    }
    return render_template("map.html", room_status=room_status)

if _name_ == '_main_':
    app.run(debug=True)