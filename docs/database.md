# Database structure

### _Table `packages`_:
__package_name__: name of the package

__build_status__: build status (0=unbuilt, 1=successful, 2=unknown error, 3=error in check(), 4=missing dependencies more reasons to come!)

__package_version__: last known package version (0=unknown, other value=version)


### _Table `users`_:
__username__: username to log in

__password_hash__: hash of the password to log in

__user_role__: user role of the user (0=administrator, 1=guest, other value=something)

## Planned (maybe, just maybe...):
### _Table_ `builds`:
__package_name__: name of the package

__build_date__: date the build happened

__build_status__: result of the build (same statuses as in table packages)

__build_duration__: duration of the build