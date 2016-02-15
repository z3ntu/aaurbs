# Create the secret key with:
#     import os
#     os.urandom(24)
# KEEP IT SECRET!
secret_key = b'paste-here'
# If flask should be started in debug mode
debug = False
# Name of the repository (has to be in client conf)
repo_name = "repo"
# Public accessible (eg by webserver) path
repo_path = "/srv/http/archlinux"
# Base path where packages, logs & database are stored
base_path = "/aur"
