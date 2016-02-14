# Database structure

### _Table `packages`_:
__package_name__: name of the package

__build_status__: build status (0=unbuilt, 1=successful, 2=fail, more reasons to come!)

__package_version__: last known package version (0=unbuilt/not defined, other value=version)


### _Table `users`_:
__username__: username to log in

__password_hash__: hash of the password to log in

__user_role__: user role of the user (0=administrator, other value=something)