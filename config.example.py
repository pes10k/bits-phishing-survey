"""Configuration options for the a tornado based web service. This
file is used to track the configuration options that are used in the web
service.  When deploying, copy this file to config.py and fill in the
configuration values accordingly."""

import os

root_dir = os.path.dirname(os.path.realpath(__file__))

# MongoDB conection parameters
mongo_params = {
    'host': 'localhost',
    'port': 27017,
    'ssl': False
}

# The database in Mongo to connect to.
mongo_database = None

ssl_options = None

# The directory that the application should write logs to.  If this directory
# does not exist, it will be created at application start up
log_dir = os.path.join(root_dir, "logs")

# The unix user account that tornado should drop down to, after binding to
# the given port.  If this is not set, the application will continue running
# as the same user who launched the process
tornado_user = None

# Whether to run tornado in debug mode.  If set to True, stack traces
# on errors will be shown to the requester, as well as logged, and other
# similar error showing functionality
debug = True

# The port that tornado should bind to and accept requests from
port = 8443

# Path to where templates are stored on disk
template_path = os.path.join(root_dir, "templates")

# Static path for serving files
static_path = os.path.join(root_dir, "static")

# Password for sending SMTP survey solicitation messages
smtp_password = None

# Host to connect to STMP server at
smtp_server = "example.org"

# Email address to send survey solication messages from
from_address = "account@example.org"
