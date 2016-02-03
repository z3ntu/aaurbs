# Automated AUR build system

These two bash scripts are designed to build AUR packages and add them to a pacman-usable repository.

## My setup:
- User `aur` which has a no-password sudo access for pacman (`aur ALL=(ALL) NOPASSWD: /usr/bin/pacman`).
- Folder `/aur/` for the two scripts, owned by user `aur`.
- Apache/httpd folder `/srv/http/archlinux/` where all built packages and the repo file are stored, owned by user `aur`.
- On the "client" an entry in `/etc/pacman.conf` with:
```
[vps]
SigLevel = Never
Server = http://<server-ip-address>/archlinux
```

### Planned
- Webinterface (Python with flask, or PHP)
- Possible rewrite in a better scripting language (very likely Python).

### Should/has to be fixed
- All VCS packages should be treated the same (right now only `-git`)
- Remove old packages from package directory (need database for that probably -> needs rewrite)!
