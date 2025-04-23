from flask import Flask, render_template, request, redirect, url_for, session, flash
from model import db, MMUBuilding, Room, User
from sqlalchemy import text
from flask_login import LoginManager, login_user, logout_user, login_required, current_user


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required if using sessions

# MySQL DB connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Hr060491#@localhost/sql_bee_events'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the db
db.init_app(app)

# Create tables once
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
            flash('Username or email already exists')
            return redirect(url_for('signup'))

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Signup successful! Please login.')
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
            flash('Logged in successfully.')
            return redirect(url_for('userpage'))  # change to your homepage
        else:
            flash('Invalid credentials')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('login'))

@app.route('/userpage')
def userpage():
    return render_template('userpage.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.form.get('query', '')  # Get the search query
    if query:
        # Search buildings and rooms
        buildings = MMUBuilding.query.filter(MMUBuilding.building_name.ilike(f"%{query}%")).all()
        rooms = Room.query.filter(Room.room_name.ilike(f"%{query}%")).all()
    else:
        buildings = MMUBuilding.query.all()
        rooms = Room.query.all()
    
    return render_template('search_results.html', buildings=buildings, rooms=rooms)

if __name__ == '__main__':
    app.run(debug=True)


