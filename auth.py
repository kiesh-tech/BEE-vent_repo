from flask import Blueprint, request, render_template

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle login logic here
        email = request.form['email']
        password = request.form['password']
        return f"Logged in as {email}"
    return render_template('login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Handle signup logic here
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        return f"Signed up as {name}"
    return render_template('signup.html')

