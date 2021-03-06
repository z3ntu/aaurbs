#!/usr/bin/env python

import json
import os
import sqlite3
import sys

import flask
import flask_login
import requests
from werkzeug.security import generate_password_hash, check_password_hash

import config
from aaurbs import AUR_BASE_PATH, LOG_PATH, REPO_PATH, add_package, remove_package


class User(flask_login.UserMixin):
    pass


app = flask.Flask(__name__)

app.secret_key = config.secret_key
login_manager = flask_login.LoginManager()
login_manager.init_app(app)


@app.route('/')
def root():
    return flask.send_from_directory('static', 'index.html')


@app.route('/api/register', methods=['POST'])
def register():
    return flask.Response("{\"status\": \"error\", \"error_message\": \"Registrations are disabled.\"}")
    username = flask.request.json.get('username')
    if len(username) > 64:
        return flask.Response(
            "{\"status\": \"error\", \"error_message\": \"Please use a username shorter than 64 characters.\"}",
            mimetype="application/json")
    if len(flask.request.json.get("pw")) > 64:
        return flask.Response(
            "{\"status\": \"error\", \"error_message\": \"Please use a password shorter than 64 characters.\"}",
            mimetype="application/json")
    passwordhash = generate_password_hash(flask.request.json.get('pw'))
    db = get_db()
    userexists = len(db.execute("SELECT username FROM users WHERE username=?", (username,)).fetchall()) != 0
    if userexists:
        return flask.Response("{\"status\": \"error\", \"error_message\": \"User already exists.\"}",
                              mimetype="application/json")
    db.execute(
        "INSERT INTO users (username, password_hash, user_role) VALUES (?, ?, ?)", (username, passwordhash, 1))
    db.commit()
    return flask.Response("{\"status\": \"ok\"}", mimetype="application/json")


@app.route('/api/login', methods=['POST'])
def login():
    username = flask.request.json.get('username')
    pass_hash = get_db().execute("SELECT password_hash FROM users WHERE username=?", (username,)).fetchone()
    if pass_hash is not None and check_password_hash(pass_hash[0], flask.request.json.get('pw')):
        user = User()
        user.id = username
        flask_login.login_user(user)
        return flask.Response("{\"status\": \"ok\"}", mimetype="application/json")

    return flask.Response("{\"status\": \"error\", \"error_message\": \"Bad login.\"}", mimetype="application/json")


@app.route('/api/logout', methods=['POST'])
def logout():
    flask_login.logout_user()
    return flask.Response("{\"status\": \"ok\"}", mimetype="application/json")


@app.route('/api/add_package', methods=['POST'])
@flask_login.login_required
def add_package_web():
    workdir = os.getcwd()  # get current working directory
    if flask_login.current_user.role != "0":
        return flask.Response("{\"status\": \"error\", \"error_message\": \"No permission.\"}",
                              mimetype="application/json")
    packagename = flask.request.json.get('package_name')
    status, error_message = add_package(packagename, get_db())
    print("Adding package '" + packagename + "', requested by user '" + flask_login.current_user.username + "'")
    os.chdir(workdir)  # get back to the original working directory
    if status:
        return flask.Response("{\"status\": \"ok\"}", mimetype="application/json")
    else:
        return flask.Response("{\"status\": \"error\", \"error_message\": \"" + error_message + "\"}",
                              mimetype="application/json")


@app.route('/api/remove_package', methods=['POST'])
@flask_login.login_required
def remove_package_web():
    if flask_login.current_user.role != "0":
        return flask.Response("{\"status\": \"error\", \"error_message\": \"No permission.\"}",
                              mimetype="application/json")
    packagename = flask.request.json.get('package_name')
    print("Removing package '" + packagename + "', requested by user '" + flask_login.current_user.username + "'")
    if remove_package(packagename, get_db()):
        return flask.Response("{\"status\": \"ok\"}", mimetype="application/json")
    else:
        return flask.Response("{\"status\": \"error\", \"error_message\": \"Package is invalid.\"}",
                              mimetype="application/json")


@app.route('/api/get_user_info', methods=['GET'])
@flask_login.login_required
def get_user_info():
    return flask.Response(json.dumps(flask_login.current_user.__dict__), mimetype="application/json")


@app.route('/api/get_packages', methods=['GET'])
def get_packages():
    db_packages = get_db().execute("SELECT * FROM packages").fetchall()
    packages = []
    for package in db_packages:
        packages.append({"package_name": package[0], "build_status": package[1], "package_version": package[2]})
    return flask.Response(json.dumps(packages), mimetype="application/json")


@app.route('/api/get_package_info', methods=['GET'])
def get_package_info():
    package_name = flask.request.args.get("package_name")
    if package_name is None:
        return flask.Response("{\"status\": \"error\", \"error_message\": \"parameter package_name is missing\"}",
                              mimetype="application/json")
    package = get_db().execute("SELECT * FROM packages WHERE package_name=?", (package_name,)).fetchone()
    if package is None:
        return flask.Response("{\"status\": \"error\", \"error_message\": \"package not found\"}",
                              mimetype="application/json")
    return flask.Response(
        json.dumps({"status": "ok", "package_name": package[0], "build_status": package[1],
                    "package_version": package[2]}),
        mimetype="application/json")


@app.route('/api/get_build_log', methods=['GET'])
def get_log():
    package_name = flask.request.args.get("package_name")
    if package_name is None:
        return flask.Response("Parameter 'package_name' is missing!", mimetype="text/plain")
    if not os.path.isdir(LOG_PATH + "/" + package_name):
        return flask.Response("Package not found.", mimetype="text/plain")
    else:
        directory = os.listdir(LOG_PATH + "/" + package_name)
        if not directory:
            return flask.Response("No logs for package were found.", mimetype="text/plain")
        directory.sort(reverse=True)
        try:
            return flask.Response(open(LOG_PATH + "/" + package_name + "/" + directory[0]).read(),
                                  mimetype="text/plain")
        except UnicodeDecodeError as e:
            return flask.Response("Error while reading the log file: " + str(e), mimetype="text/plain")


@app.route('/api/download_file/<package_name>', methods=['GET'])
def download_file(package_name):
    package_version = get_db().execute(
        "SELECT package_version FROM packages WHERE package_name=?", (package_name,)).fetchone()
    if package_version is None:
        return flask.Response("Package not found.", mimetype="text/plain")
    package_version = package_version[0]
    for file in os.listdir(REPO_PATH):
        if file.endswith(".pkg.tar.xz") and file.startswith(package_name + "-" + package_version):
            return flask.send_file(REPO_PATH + "/" + file, as_attachment=True, attachment_filename=file)
    return flask.Response("Binary package not found.", mimetype="text/plain")


@app.route('/api/check_orphans', methods=['GET'])
@flask_login.login_required
def check_orphans():
    db_packages = get_db().execute("SELECT package_name FROM packages").fetchall()
    good_packages = []
    broken_packages = []
    request_url = "https://aur.archlinux.org/rpc/?v=5&type=info"
    for package in db_packages:
        request_url += "&arg[]=" + package[0]
        broken_packages.append(package[0])  # all packages are guilty until they are proven innocent
    resp = requests.get(request_url)
    for package_obj in resp.json()["results"]:
        package = package_obj["Name"]
        print(package)
        good_packages.append(package)
        broken_packages.remove(package)
    return flask.Response(json.dumps({"good": good_packages, "broken": broken_packages}), mimetype="text/plain")


@app.route('/<path:filename>')
def catch_all(filename):
    return flask.send_from_directory('static', filename)


@login_manager.user_loader  # should create user object (get from database etc)
def user_loader(username):
    print("=== user_loader ===")
    userdb = get_db().execute("SELECT * FROM users WHERE username=?", (username,))
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
    return flask.Response("{\"status\": \"error\", \"error_message\": \"Not authorized.\"}",
                          mimetype="application/json")


def get_db():
    if not hasattr(flask.g, 'sqlite_db'):
        flask.g.sqlite_db = sqlite3.connect(AUR_BASE_PATH + "/aaurbs.db")
    return flask.g.sqlite_db


if __name__ == '__main__':
    try:
        if config.use_wsgi:
            app.run(debug=config.debug)
        else:
            if config.use_ssl:
                ssl_context = ('server.crt', 'server.key')
            else:
                ssl_context = None
            app.run(host=config.host,
                    port=config.port,
                    ssl_context=ssl_context,
                    debug=config.debug)
    except OSError as err:
        print("[ERROR] " + err.strerror, file=sys.stderr)
        print("[ERROR] The program will now terminate.", file=sys.stderr)
