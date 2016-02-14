import flask
from aaurbs import AUR_BASE_PATH, add_package, LOG_PATH
import sys
import os
import json
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

    @app.route('/api/register', methods=['POST'])
    def register():
        # TODO: SQL injection proof
        # TODO: Check if user already exists!
        username = flask.request.json.get('username')
        passwordhash = generate_password_hash(flask.request.json.get('pw'))
        db = get_db()
        db.execute("INSERT INTO users (username, password_hash, user_role) VALUES ('" + username + "', '" + passwordhash + "', '1')")
        db.commit()
        return flask.Response("{\"status\": \"ok\"}", mimetype="application/json")

    @app.route('/api/login', methods=['POST'])
    def login():
        username = flask.request.form['username']
        if check_password_hash(get_db().execute("SELECT password_hash FROM users WHERE username='"+username+"'").fetchone()[0], flask.request.form['pw']):
            user = User()
            user.id = username
            flask_login.login_user(user)
            return flask.redirect("#/protected")

        return flask.Response("{\"status\": \"error\", \"error_message\": \"Bad login.\"}", mimetype="application/json")

    @app.route('/api/logout', methods=['POST'])
    def logout():
        flask_login.logout_user()
        return 'Logged out'

    @app.route('/api/add_package', methods=['POST'])
    @flask_login.login_required
    def add_package_web():
        packagename = flask.request.json.get('package_name')
        status, error_message = add_package(packagename, get_db())
        print("Adding package '" + packagename + "', requested by user '" + flask_login.current_user.username + "'")
        if status:
            return flask.Response("{\"status\": \"ok\"}", mimetype="application/json")
        else:
            return flask.Response("{\"status\": \"error\", \"error_message\": \""+error_message+"\"}", mimetype="application/json")

    @app.route('/api/get_user_info')
    @flask_login.login_required
    def get_user_info():
        return flask.Response(json.dumps(flask_login.current_user.__dict__), mimetype="application/json")

    @app.route('/api/get_packages')
    def get_packages():
        db_packages = get_db().execute("SELECT * FROM packages").fetchall()
        packages = []
        for package in db_packages:
            packages.append({"package_name": package[0], "build_status": package[1], "package_version": package[2]})
        return flask.Response(json.dumps(packages), mimetype="application/json")

    @app.route('/api/get_package_info')
    def get_package_info():
        package_name = flask.request.args.get("package_name")
        if package_name is None:
            return "{\"error\": \"parameter package_name is missing\"}"
        package = get_db().execute("SELECT * FROM packages WHERE package_name='"+package_name+"'").fetchone()
        if package is None:
            return "{\"error\": \"package not found\"}"
        return flask.Response(json.dumps({"package_name": package[0], "build_status": package[1], "package_version": package[2]}), mimetype="application/json")

    @app.route('/api/get_build_log')
    def get_log():
        package_name = flask.request.args.get("package_name")
        if package_name is None:
            return "{\"error\": \"parameter package_name is missing\"}"
        if not os.path.isdir(LOG_PATH + "/" + package_name):
            return "{\"error\": \"package not found\"}"
        else:
            directory = os.listdir(LOG_PATH + "/" + package_name)
            if not directory:
                return "{\"error\": \"no logs for package found\"}"
            directory.sort(reverse=True)
            return flask.Response(open(LOG_PATH + "/" + package_name + "/" + directory[0]).read(), mimetype="text/plain")

    @app.route('/<path:filename>')
    def catch_all(filename):
        print("Catch-all: " + filename)
        return flask.send_from_directory('static', filename)

    @app.route('/protected')
    @flask_login.login_required
    def protected():
        return 'Logged in as: ' + flask_login.current_user.username + "\nRole: " + flask_login.current_user.role

    @login_manager.user_loader  # should create user object (get from database etc)
    def user_loader(username):
        print("=== user_loader ===")
        userdb = get_db().execute("SELECT * FROM users WHERE username='"+username+"'")
        if userdb is None:
            return

        user = User()
        user.username = username
        user.role = userdb.fetchone()[2]
        return user

    @login_manager.request_loader  # gets called when unauthorized, additional authorization methods
    def request_loader(request):
        print("=== request_loader ===")
        print(request.method + " - " + request.remote_addr)
        return None

    @login_manager.unauthorized_handler
    def unauthorized_handler():
        return flask.Response("{\"error\": \"not authorized\"}", mimetype="application/json")

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
