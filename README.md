# Automated AUR build system

aaurbs is designed to automatically build AUR packages and add them to a pacman-usable repository.

## Setup:
- User `aur` which has a no-password sudo access for pacman (`aur ALL=(ALL) NOPASSWD: /usr/bin/pacman`).
- Folder `/aur/` for the two scripts, owned by user `aur`.
- Apache/httpd folder `/srv/http/archlinux/` where all built packages and the repo file are stored, owned by user `aur`.
- On the "client" an entry in `/etc/pacman.conf` with:
```
[db-name]
SigLevel = Never
Server = http://<server-ip-address>/archlinux
```
_Note, that `db-name` has to match `repo_name` in `config.py`!__

## Requirements
- [Python 3](https://www.python.org/)
- [Flask](http://flask.pocoo.org/)
- [Flask-login](https://github.com/maxcountryman/flask-login)
- `xdelta3` **if** `delta` in `config.py` is set to `True`

```
pacman -S python python-flask python-flask-login # and maybe xdelta3
```

## Start
- Modify `aaurbs.service` & `aaurbs_webserver.service` to your location.
- Copy/symlink `aaurbs.service`, `aaurbs.timer` and `aaurbs_webserver.service` to `/etc/systemd/system/`
- To start `aaurbs` manually: `systemctl start aaurbs.service`
- To autostart `aaurbs` every hour (persists after reboot): `systemctl enable --now aaurbs.timer`
- To start `aaurbs_webserver` manually: `systemctl start aaurbs_webserver.service`
- To autostart `aaurbs_webserver` automatically (after reboot): `systemctl enable --now aaurbs_webserver.service`
- The webservice will be available on port you configured in `config.py` (default: `8080`)