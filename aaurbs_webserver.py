# from flask import Flask, request, send_from_directory
import flask
# import aaurbs
from aaurbs import AUR_BASE_PATH
import sys
import os
import config
import sqlite3
import flask.ext.login as flask_login
from werkzeug.security import generate_password_hash, check_password_hash

class User(flask_login.UserMixin):
    pass


def main():
    app = flask.Flask(__name__)

    app.secret_key = config.secret_key
    login_manager = flask_login.LoginManager()
    login_manager.init_app(app)

    @app.route('/')
    def root():
        return flask.send_from_directory('static', 'index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if flask.request.method == 'GET':
            return flask.send_from_directory("static", "login.html")

        username = flask.request.form['username']
        if check_password_hash(get_db().execute("SELECT password_hash FROM users WHERE username='"+username+"'").fetchone()[0], flask.request.form['pw']):
            user = User()
            user.id = username
            flask_login.login_user(user)
            return flask.redirect(flask.url_for('protected'))

        return 'Bad login'

    @app.route('/api/add_package', methods=['POST'])
    @flask_login.login_required
    def add_package():
        print("hi")
        return 'OK'

    @app.route('/<path:filename>')
    def catch_all(filename):
        print(filename)
        return flask.send_from_directory('static', filename)

    @app.route('/protected')
    @flask_login.login_required
    def protected():
        return 'Logged in as: ' + flask_login.current_user.id

    @app.route('/logout')
    def logout():
        flask_login.logout_user()
        return 'Logged out'

    @login_manager.user_loader  # should create user object (get from database etc)
    def user_loader(username):
        print("=== user_loader ===")
        if get_db().execute("SELECT * FROM users WHERE username='"+username+"'") is None:
            return

        user = User()
        user.id = username
        return user

    @login_manager.request_loader  # gets called when unauthorized, additional authorization methods
    def request_loader(request):
        print("=== request_loader ===")
        print(request.method + " - " + request.remote_addr)
        return None

    @login_manager.unauthorized_handler
    def unauthorized_handler():
        return flask.send_from_directory("static", "unauthorized.html")

    # ACTUAL METHOD
    try:
        app.run(host='0.0.0.0',
                port=8080,
                debug=True)
    except OSError as err:
        print("[ERROR] " + err.strerror, file=sys.stderr)
        print("[ERROR] The program will now terminate.", file=sys.stderr)


def get_db():
    if not hasattr(flask.g, 'sqlite_db'):
        flask.g.sqlite_db = sqlite3.connect(AUR_BASE_PATH + "/aaurbs.db")
    return flask.g.sqlite_db

if __name__ == '__main__':
    main()
