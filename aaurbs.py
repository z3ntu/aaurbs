#!/usr/bin/env python

import os
import pwd
import grp
import sqlite3
import subprocess
import shutil
import re
from time import strftime, gmtime

AUR_BASE_PATH = "/aur"
PACKAGES_PATH = AUR_BASE_PATH + "/packages"
PKGDEST = "/srv/http/archlinux"
LOG_PATH = AUR_BASE_PATH + "/logs"

REPO_PATH = "/srv/http/archlinux"
REPO_FILE = REPO_PATH + "/vps.db.tar.gz"


def main():
    global database
    database = sqlite3.connect(AUR_BASE_PATH + "/aaurbs.db")
    change_workdir(PACKAGES_PATH)
    set_user("luca")
    create_directories()
    create_database(database)
    # test()
    # add_package("f3")
    # add_package("f3-git")
    update_packages()
    save_database(database)


def test():
    add_package("f3")
    build_package("f3")


def create_database(conn):
    print("Creating database (if not exists).")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS packages (
            package_name VARCHAR(100),
            build_status VARCHAR(2),
            package_version VARCHAR(50),
            PRIMARY KEY (package_name)
        );
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username VARCHAR(100),
            password_hash VARCHAR(100),
            user_role VARCHAR(2),
            PRIMARY KEY (username)
        )
    """)


def save_database(conn):
    conn.commit()
    conn.close()


def change_workdir(directory):
    os.chdir(directory)


def add_package(name):
    if not os.path.isdir(name):
        output = subprocess.check_output("git clone -q https://aur.archlinux.org/" + name + ".git", shell=True,
                                         stderr=subprocess.STDOUT).decode("utf-8")
        if output == "warning: You appear to have cloned an empty repository.\n":
            if os.path.isdir(PACKAGES_PATH + "/" + name):
                shutil.rmtree(PACKAGES_PATH + "/" + name)
            print("Package does not exist!")
            return
        else:
            database.execute(
                "INSERT INTO packages (package_name, build_status, package_version) VALUES ('" + name + "', '0', '0');")
            database.commit()
            print("Package successfully added.")
            os.makedirs(LOG_PATH + "/name", exist_ok=True)
    else:
        print("Package '" + name + "' already added.")
        return


def remove_package(name):
    if os.path.isdir(PACKAGES_PATH + "/" + name):
        shutil.rmtree(PACKAGES_PATH + "/" + name)
        database.execute("DELETE FROM packages WHERE package_name='" + name + "'")
        print("Removed package '" + name + "'")
    else:
        print("Package '" + name + "' is invalid.")


def build_package(name):
    print("Building package '" + name + "'.")
    change_workdir(PACKAGES_PATH + "/" + name)
    try:
        output = subprocess.check_output("PKGDEST='" + PKGDEST + "' makepkg -src --noconfirm --noprogressbar",
                                         shell=True,
                                         stderr=subprocess.STDOUT).decode("utf-8")
    except subprocess.CalledProcessError as e:  # non-zero exit code
        if b"ERROR: A package has already been built." in e.output:
            print("Warning: Package has already been built.")
        else:
            print(e.output)
            log_to_file(LOG_PATH + "/" + name + "/" + strftime("%Y-%m-%d_%H:%M:%S", gmtime()) + ".log", e.output)
            database.execute("UPDATE packages SET build_status=2 WHERE package_name='" + name + "'")
        return
    change_workdir(PACKAGES_PATH)
    # save output into logfile
    log_to_file(LOG_PATH + "/" + name + "/" + strftime("%Y-%m-%d_%H:%M:%S", gmtime()) + ".log", output)

    new_version = re.search('Finished making: ' + name + ' (.+?) \(', output).group(1)

    for file in os.listdir(PKGDEST):
        if name in file:
            version = re.search(name + '-(.+?)-(x86_64|i686|any).pkg.tar.xz', file).group(1)
            if new_version != version:  # skip old packages
                continue
            print("VERSION: " + version)
            print(file)
            database.execute(
                "UPDATE packages SET build_status=1, package_version='" + version + "' WHERE package_name='" + name + "'")
            add_to_repo(REPO_PATH + "/" + file)
            break


def add_to_repo(filename):
    print("Adding " + filename + " to database.")
    # the --remove parameter automatically removes old files!! :)
    output = subprocess.check_output("repo-add --remove " + REPO_FILE + " " + filename,
                                     shell=True,
                                     stderr=subprocess.STDOUT).decode("utf-8")
    log_to_file(LOG_PATH + "/repo-add.log", output)


def update_packages():
    for package in os.listdir(PACKAGES_PATH):
        change_workdir(PACKAGES_PATH + "/" + package)
        output = subprocess.check_output("git pull",
                                         shell=True,
                                         stderr=subprocess.STDOUT).decode("utf-8")
        if output != "Already up-to-date.\n":  # new version
            build_package(package)
        elif re.search('-(bzr|git|hg|svn)', package):  # vcs package
            build_package(package)
        elif database.execute("SELECT build_status FROM packages WHERE package_name='" + package + "'").fetchone()[0] != "1":  # package status is not successful
            build_package(package)
        else:
            print("Package '" + package + "' is already up-to-date.")


def set_user(name):
    uid = pwd.getpwnam(name)[2]
    gid = grp.getgrnam(name)[2]
    os.setgid(gid)
    os.setuid(uid)


def create_directories():
    os.makedirs(AUR_BASE_PATH, exist_ok=True)
    os.makedirs(PACKAGES_PATH, exist_ok=True)
    os.makedirs(LOG_PATH, exist_ok=True)
    os.makedirs(REPO_PATH, exist_ok=True)
    os.makedirs(PKGDEST, exist_ok=True)


def log_to_file(filename, content):
    logfile = open(filename, "w")
    logfile.write(content)
    logfile.close()


if __name__ == '__main__':
    main()