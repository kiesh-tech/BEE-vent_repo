from flask import Flask, render_template, request, redirect, url_for, session
from model import db, MMUBuilding, Room, User, Event
from flask_login import LoginManager, login_user, logout_user, login_required, current_user


app = Flask(__name__)
app.secret_key = 'beeevents3'

# MySQL DB connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Hr060491#@localhost/sql_bee_events'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the db
db.init_app(app)

with app.app_context():
    db.create_all()

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

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
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
        else:
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/userpage')
def userpage():
    return render_template('userpage.html')

@app.route('/join')
def join():
    return render_template('join.html')

@app.route('/comment')
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
    name = request.form['event_name']
    date = request.form['date']
    event_type = request.form['event_type']
    location = request.form['location']
    venue_code = request.form['venue_code']
    organizer = request.form['organizer']
    time = request.form['time']
    capacity = request.form['capacity']

    new_event = Event(
        name=name,
        date=date,
        event_type=event_type,
        location=location,
        venue_code=venue_code,
        organizer=organizer,
        time=time,
        capacity=capacity,
        created_by=current_user.id
    )
    db.session.add(new_event)
    db.session.commit()
    
    return redirect(url_for('userpage'))

if __name__ == '__main__':
    app.run(debug=True)


