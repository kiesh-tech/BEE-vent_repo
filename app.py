from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle login logic here
        email = request.form['email']
        password = request.form['password']
        return f"Logged in as {email}"
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Handle signup logic here
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        return f"Signed up as {name}"
    return render_template('signup.html')


if __name__ == '__main__':
    app.run(debug=True)


