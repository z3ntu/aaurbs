# Automated AUR build system

aaurbs is designed to automatically build AUR packages and add them to a pacman-usable repository.

## Setup:
- User `aur` which has a no-password sudo access for pacman and other neccessary utilities (`aur ALL=(ALL) NOPASSWD: /usr/bin/pacman, /usr/bin/mkarchroot, /usr/bin/arch-nspawn, /usr/bin/makechrootpkg`).
- Folder `/aur/` for the the packages & logs, owned by user `aur`.
- Apache/httpd folder `/srv/http/archlinux/` where all built packages and the repo files are stored, owned by user `aur`.
- On the "client" an entry in `/etc/pacman.conf` with:
```
[db-name]
SigLevel = Never
Server = http://<server-ip-address>/archlinux
```
_Note, that `db-name` has to match `repo_name` in `config.py`!
- Execute `bower update` in the `static` directory to install all bower components!

## Requirements
- [Python 3](https://www.python.org/)
- [Flask](http://flask.pocoo.org/)
- [Flask-login](https://github.com/maxcountryman/flask-login)
- `xdelta3` **if** `delta` in `config.py` is set to `True`
- Apache if you want to use WSGI (you do!)
```
pacman -S python python-flask python-flask-login # and maybe xdelta3
```

## Start
- Modify `aaurbs.service` & `aaurbs_webserver.service` to match your location of the application.
- Copy/symlink `aaurbs.service`, `aaurbs.timer` and `aaurbs_webserver.service` to `/etc/systemd/system/`
- To start `aaurbs` manually: `systemctl start aaurbs.service`
- To autostart `aaurbs` every hour (persists after reboot): `systemctl enable --now aaurbs.timer`
- To start `aaurbs_webserver` manually: `systemctl start aaurbs_webserver.service`
- To autostart `aaurbs_webserver` automatically (after reboot): `systemctl enable --now aaurbs_webserver.service`
- The webservice will be available on port you configured in `config.py` (default: `8080`)

## How to setup WSGI with Apache
- [Setup mod_wsgi](https://wiki.archlinux.org/index.php/Mod_wsgi)
- Place this repo in `/srv/http/aaurbs`
- Copy/symlink the `wsgi-aaurbs.conf` file to `/etc/httpd/conf/extra/`
- Place the line `Include conf/extra/wsgi-aaurbs.conf` somewhere at the end of `/etc/httpd/conf/httpd.conf`
- Note that some parts of the part "Start" is not valid with this method. If you need help, please file an issue or contact me.


Please note, that `PKGEXT` has to be `PKGEXT='.pkg.tar.xz'` in `/etc/makepkg.conf`.
