#!/usr/bin/env python

import os
import pwd
import grp
import sqlite3
import subprocess
import shutil

AUR_PATH = "/aur"
database = None


def main():
    change_workdir(AUR_PATH)
    set_user("luca")
    global database
    database = sqlite3.connect('aaurbs.db')
    create_database(database)
    add_package("f3-git")
    save_database(database)


def create_database(conn):
    print("Creating database (if not exists).")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS aaurbs (
            package_name VARCHAR(100),
            build_status VARCHAR(100),
            package_version VARCHAR(50)
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
            if os.path.isdir(AUR_PATH + "/" + name):
                shutil.rmtree(AUR_PATH + "/" + name)
            print("Package does not exist!")
            return
        else:
            database.execute("INSERT INTO aaurbs (package_name, build_status, package_version) VALUES ('"+name+"', '0', '0');")
            print("Package successfully added.")
    else:
        print("Package '" + name + "' already added.")
        return


def set_user(name):
    uid = pwd.getpwnam(name)[2]
    gid = grp.getgrnam(name)[2]
    os.setgid(gid)
    os.setuid(uid)


if __name__ == '__main__':
    main()
