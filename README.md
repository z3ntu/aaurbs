# Automated AUR build system

aaurbs is designed to build AUR packages and add them to a pacman-usable repository.

## Setup:
- User `aur` which has a no-password sudo access for pacman (`aur ALL=(ALL) NOPASSWD: /usr/bin/pacman`).
- Folder `/aur/` for the two scripts, owned by user `aur`.
- Apache/httpd folder `/srv/http/archlinux/` where all built packages and the repo file are stored, owned by user `aur`.
- On the "client" an entry in `/etc/pacman.conf` with:
```
[<db-name>]
SigLevel = Never
Server = http://<server-ip-address>/archlinux
```
_Note, that `db-name` has to match the filename (`db-name.db.tar.gz`) in `updateall.sh`!_

## Requirements
- [Python 3](https://www.python.org/)
- [Flask](http://flask.pocoo.org/)
- [Flask-login](https://github.com/maxcountryman/flask-login)