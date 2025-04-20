from flask import Flask, render_template

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'goat'


    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    @app.route('/about')
    def about():
        return render_template('about.html')


    if __name__ == '__main__':
        app.run(debug=True)

        return app


