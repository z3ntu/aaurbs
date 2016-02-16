# API

### add_package
__POST__ `http://localhost/api/add_package`
Parameter in body: `package_name`
Response: `status` (`ok` or `error`, if `error`, an additional `error` parameter will be sent).

### get_user_info
__GET__ `http://localhost/api/get_user_info`
Response: `role`, `username`

### get_packages
__GET__ `http://localhost/api/get_packages`
Response: Array of objects with `package_version`, `build_status` & `package_name`

### get_package_info
__GET__ `http://localhost/api/get_package_info`
GET Parameters: `package_name`

### get_build_log
__GET__ `http://localhost/api/get_build_log`
GET Parameters: `package_name`

# WIP