# --- MAIN APPLICATION ---
# Create the secret key with:
#     import os
#     os.urandom(24)
# KEEP IT SECRET!
secret_key = b'paste-here'
# Name of the repository (has to be in the client conf)
repo_name = "repo"
# Public accessible (eg by webserver) path
repo_path = "/srv/http/archlinux"
# Base path where packages, logs & database are stored
base_path = "/aur"
# Use delta? Please refer to https://wiki.archlinux.org/index.php/Deltup for more information.
delta = False

# --- WEBSERVER ---
# If flask should be started in debug mode
debug = False
# Use WSGI? If yes, the options under this are all invalid and you have to have WSGI configured
use_wsgi = True
# Port to run the webserver
port = 8080
# Host (use 0.0.0.0 to listen on all interfaces, just modify it if you know what you are doing!)
host = '0.0.0.0'

# Should the webserver be secured with ssl? If yes, there has to be a server.crt & server.key file.
use_ssl = False
