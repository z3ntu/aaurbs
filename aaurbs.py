#!/usr/bin/env python
import glob
import grp
import os
import pwd
import re
import shutil
import sqlite3
import subprocess
from time import strftime, gmtime

import pkgbuild

import config

AUR_BASE_PATH = config.base_path
PACKAGES_PATH = AUR_BASE_PATH + "/packages"
LOG_PATH = AUR_BASE_PATH + "/logs"

REPO_PATH = config.repo_path
REPO_FILE = REPO_PATH + "/" + config.repo_name + ".db.tar.gz"

database = None
delta = ""


def main():
    global database
    database = sqlite3.connect(AUR_BASE_PATH + "/aaurbs.db")
    global delta
    if config.delta:
        delta = "--delta"
    else:
        delta = ""
    change_workdir(PACKAGES_PATH)
    # set_user(config.aur_user)
    create_directories()
    create_database(database)
    update_packages()
    save_database(database)
    print("End of aaurbs.py")


def create_database(conn):
    print("Creating database (if not exists).")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS packages (
            package_name VARCHAR(100),
            build_status VARCHAR(2),
            package_version VARCHAR(50),
            PRIMARY KEY (package_name)
        );
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


def add_package(name, db):
    if not os.path.isdir(PACKAGES_PATH + "/" + name):
        change_workdir(PACKAGES_PATH)
        output = subprocess.check_output(["git", "clone", "-q", "https://aur.archlinux.org/" + name + ".git"],
                                         stderr=subprocess.STDOUT).decode("utf-8")
        if output == "warning: You appear to have cloned an empty repository.\n":
            if os.path.isdir(PACKAGES_PATH + "/" + name):
                shutil.rmtree(PACKAGES_PATH + "/" + name)
            print("Package does not exist!")
            return False, "Package does not exist!"
        else:
            db.execute("INSERT INTO packages (package_name, build_status, package_version) VALUES (?, ?, ?)",
                       (name, 0, 0))
            db.commit()
            print("Package successfully added.")
            os.makedirs(LOG_PATH + "/" + name, exist_ok=True)
            return True, ""
    else:
        print("Package '" + name + "' already added.")
        return False, "Package was already added."


def remove_package(name, db):
    if os.path.isdir(PACKAGES_PATH + "/" + name):
        shutil.rmtree(PACKAGES_PATH + "/" + name)
        if os.path.isdir(LOG_PATH + "/" + name):
            shutil.rmtree(LOG_PATH + "/" + name)
        else:
            print("Could find log directory of '" + name + "'")
        db.execute("DELETE FROM packages WHERE package_name=?", (name,))
        db.commit()
        repofilelist = glob.glob(REPO_PATH + "/" + name + "-*")
        if repofilelist:
            for f in repofilelist:
                print("Removing file: " + f)
                os.remove(f)
        else:
            print("Could not find binary packages for '" + name + "'")
        output = subprocess.check_output(["repo-remove", REPO_FILE, name],
                                         stderr=subprocess.STDOUT).decode("utf-8")
        print(output)
        print("Removed package '" + name + "'")
        return True
    else:
        print("Package '" + name + "' is invalid.")
        return False


def build_package(name, clean="c", srcinfo=None):
    print("Building package '" + name + "'.")
    change_workdir(PACKAGES_PATH + "/" + name)
    if srcinfo is None:
        srcinfo = pkgbuild.SRCINFO(".SRCINFO").content
    try:
        env = os.environ.copy()
        env["PKGDEST"] = REPO_PATH
        output = subprocess.check_output(
            ["makepkg", "-sr" + clean, "--noconfirm", "--noprogressbar"],
            env=env,
            stderr=subprocess.STDOUT).decode("utf-8")
    except subprocess.CalledProcessError as e:  # non-zero exit code
        if b"ERROR: A package has already been built." in e.output:
            print("Warning: Package has already been built.")  # This is no error!
            error_status = "1"
        elif b"ERROR: The package group has already been built." in e.output:
            print("Warning: The package group has already been built.")  # Same as above.
            error_status = "1"
        elif b"ERROR: A failure occurred in check()." in e.output:
            print("ERROR: A failure occurred in check().")
            error_status = "3"
        elif b"ERROR: 'pacman' failed to install missing dependencies." in e.output:
            print("ERROR: 'pacman' failed to install missing dependencies.")
            error_status = "4"
        elif b"ERROR: One or more files did not pass the validity check!" in e.output:
            print("ERROR: One or more files did not pass the validity check!")
            error_status = "5"
        elif b"ERROR: One or more PGP signatures could not be verified!" in e.output:
            print("ERROR: One or more PGP signatures could not be verified!")
            error_status = "6"
        else:
            print(e.output)
            error_status = "2"
        log_to_file(LOG_PATH + "/" + name + "/" + strftime("%Y-%m-%d_%H:%M:%S", gmtime()) + ".log",
                    e.output.decode("utf-8"))
        database.execute("UPDATE packages SET build_status=? WHERE package_name=?", (error_status, name))
        return error_status
    change_workdir(PACKAGES_PATH)
    # save output into logfile
    log_to_file(LOG_PATH + "/" + name + "/" + strftime("%Y-%m-%d_%H:%M:%S", gmtime()) + ".log", output)

    found = False
    new_version = re.search('Finished making: ' + name + ' (.+?) \(', output).group(1)

    if type(srcinfo.get("pkgname")) is list:
        print("Split package!")
        for file in os.listdir(REPO_PATH):
            for pkgnamemember in srcinfo.get("pkgname"):
                if pkgnamemember in file:
                    version = re.search(pkgnamemember + '-(.+?)-(x86_64|i686|armv6h|armv7h|aarch64|arm|any).pkg.tar.xz',
                                        file).group(1)
                    if new_version != version:  # skip old packages
                        continue
                    print("VERSION: " + version)
                    print(file)
                    add_to_repo(REPO_PATH + "/" + file)
                    found = True
    else:
        for file in os.listdir(REPO_PATH):
            if name in file:
                version = re.search(name + '-(.+?)-(x86_64|i686|armv6h|armv7h|aarch64|arm|any).pkg.tar.xz', file).group(
                    1)
                if new_version != version:  # skip old packages
                    continue
                print("VERSION: " + version)
                add_to_repo(REPO_PATH + "/" + file)
                found = True
    if found:
        database.execute(
            "UPDATE packages SET build_status=1, package_version=? WHERE package_name=?", (version, name))
        database.commit()
        return "1"
    return "2"


def add_to_repo(filename):
    print("Adding " + filename + " to database.")
    # the --remove parameter automatically removes old files!! :)
    try:
        if delta:  # TODO: Make better?
            command = ["repo-add", "--remove", delta, REPO_FILE, filename]
        else:
            command = ["repo-add", "--remove", REPO_FILE, filename]
        output = subprocess.check_output(command,
                                         stderr=subprocess.STDOUT).decode("utf-8")
    except subprocess.CalledProcessError as e:
        print(e)
        output = e.output.decode('utf-8')
        print(e.output.decode('utf-8'))
    log_to_file(LOG_PATH + "/repo-add.log", output, mode="a")


def update_packages():
    for package in os.listdir(PACKAGES_PATH):
        change_workdir(PACKAGES_PATH)
        try:
            output = subprocess.check_output(["git", "-C", package, "pull"],
                                             stderr=subprocess.STDOUT).decode("utf-8")
        except subprocess.CalledProcessError as e:
            if "error: Your local changes to the following files would be overwritten by merge" in e.output.decode(
                    'utf-8'):
                print(os.getcwd())
                change_workdir(PACKAGES_PATH)
                try:
                    print("Resetting the root package dir!")
                    subprocess.check_output(["git", "-C", package, "fetch", "-all"])
                    subprocess.check_output(["git", "-C", package, "reset", "--hard", "origin/master"])
                    output = "Succesfully pulled!"
                except Exception as ex:
                    print(ex)
                    continue
            else:
                print(e)
                print(e.output.decode('utf-8'))
                continue
        print(package)
        if output != "Already up-to-date.\n":  # new version
            build_package(package)
        elif database.execute("SELECT build_status FROM packages WHERE package_name=?", (package,)).fetchone()[
            0] != "1":  # package status is not successful
            if re.search('-(bzr|git|hg|svn)', package):
                build_package(package, clean="")
            else:
                build_package(package)
        elif re.search('-(bzr|git|hg|svn)', package):  # vcs packages
            check_vcs(package)
            # else:
            #    print("Package '" + package + "' is already up-to-date.")


def check_vcs(package):
    srcinfo = pkgbuild.SRCINFO(package + "/.SRCINFO").content
    folder = pkgbuild.parse_source_field(srcinfo.get("source"), pkgbuild.SourceParts.folder)
    if type(srcinfo.get("source")) is not str:  # TODO: Handle multiple source attributes
        print("(Probably) multiple source attributes.")
        build_package(package, clean="", srcinfo=srcinfo)
        return
    url_folder = pkgbuild.parse_source_field(srcinfo.get("source"), pkgbuild.SourceParts.url).rsplit('/', 1)[
        -1].replace(".git", "")
    if folder is None:
        folder = url_folder
    if not os.path.isdir(package + "/src") or not os.path.isdir(package + "/" + folder):
        print("Building VCS package the first time.")
        build_package(package, clean="", srcinfo=srcinfo)
    elif re.search('-git', package):
        try:
            output = subprocess.check_output(
                ["git", "-C", package + "/src/" + folder, "fetch"],
                stderr=subprocess.STDOUT).decode("utf-8")  # TODO: Test if this actually works.
        except subprocess.CalledProcessError as e:
            database.execute("UPDATE packages SET build_status=? WHERE package_name=?", (2, package))
            database.commit()
            print("ERROR WHILE UPDATING, some file probably got changed and I have no idea how to fix this!")
            print("not right now (running 'git reset --hard') - but building normally to see if it works!")
            if "Please, commit your changes or stash them before you can merge." in e.output.decode('utf-8'):
                build_package(package, clean="", srcinfo=srcinfo)
            print(e)
            print(e.output.decode('utf-8'))
            return
        if output != "":
            print("Updating package '" + package + "'.")
            build_package(package, clean="", srcinfo=srcinfo)
        else:
            print(output)
            print("-git package '" + package + "' is already up-to-date.")
    else:
        build_package(package, clean="", srcinfo=srcinfo)  # other vcs sources


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


def log_to_file(filename, content, mode="w"):
    logfile = open(filename, mode=mode, encoding="utf-8")
    logfile.write(content)
    logfile.close()


if __name__ == '__main__':
    main()
