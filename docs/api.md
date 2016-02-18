# API

- [login](#login)

### login
__POST__ `/api/login`
Parameter in body: `username`, `pw`
Response: `status`: `ok`/`error`, if `error`: `error_message`

### logout
__POST__ `/api/logout`
Response: `status`: `ok`

### register
__POST__ `/api/register`
Parameter in body: `username`, `pw`
Response: `status`: `ok`/`error`, if `error`: `error_message`

### add_package
_NEEDS AUTHENTICATION_
__POST__ `/api/add_package`
Parameter in body: `package_name`
Response: `status`: `ok`/`error`, if `error`: `error_message`

### remove_package
_NEEDS AUTHENTICATION_
__POST__ `/api/remove_package`
Parameter in body: `package_name`
Response: `status`: `ok`/`error`, if `error`: `error_message`

### get_user_info
_NEEDS AUTHENTICATION_
__GET__ `/api/get_user_info`
Response: `username`, `role`

### get_packages
__GET__ `/api/get_packages`
Response: Array of objects with: (`package_name`, `build_status`, `package_version`)

### get_package_info
__GET__ `/api/get_package_info`
GET Parameters: `package_name`
Response: `status`: `ok`/`error`, if `error`: `error_message`; if `ok`: `package_name`, `build_status`, `package_version`

### get_build_log
__GET__ `/api/get_build_log`
GET Parameters: `package_name`
Response: Plain text with: log or error message

### download_file
__GET__ `/api/download_file/<package_name>`
Parameter is in URL.
Response: File or plain text error reason