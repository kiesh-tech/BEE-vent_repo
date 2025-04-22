from flask import Flask, render_template, request, redirect, url_for, session
from model import db, MMUBuilding, Room
from sqlalchemy import text

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required if using sessions

# MySQL DB connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Hr060491#@localhost/sql_bee_events'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the db
db.init_app(app)

with app.app_context():
    try:
        db.session.execute(text('SELECT 1'))
        print("✅ MySQL database connected successfully!")
    except Exception as e:
        print("❌ Database connection failed:", e)


# Create tables once
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        return f"Logged in as {email}"
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        return f"Signed up as {name}"
    return render_template('signup.html')

@app.route('/userpage')
def userpage():
    return render_template('userpage.html')

@app.route('/buildings')
def buildings():
    # Query all buildings from the database
    buildings = MMUBuilding.query.all()  # .all() fetches all rows from the 'MMUBuilding' table
    return render_template('buildings.html', buildings=buildings)

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


