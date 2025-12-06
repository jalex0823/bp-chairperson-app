"""
DreamHost Passenger WSGI entry point.

This file activates the virtual environment and exposes the Flask WSGI `application`.
Place this file in the web app directory where DreamHost's Passenger expects the app.
"""
import os
import sys

# Adjust these paths as needed on the DreamHost server
VENV_ACTIVATE = os.path.expanduser('~/backporch-venv/bin/activate_this.py')

# Ensure the app path is on sys.path (this directory contains app.py)
APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

# Activate virtualenv
if os.path.exists(VENV_ACTIVATE):
    with open(VENV_ACTIVATE, 'r') as f:
        code = compile(f.read(), VENV_ACTIVATE, 'exec')
        exec(code, {'__file__': VENV_ACTIVATE})

# Optionally set environment variables here if not using .env
# os.environ['FLASK_ENV'] = 'production'
# os.environ['DATABASE_URL'] = 'mysql+pymysql://chairperson:***@mysql.therealbackporch.com:3306/chairameeting?charset=utf8mb4'
# os.environ['MAIL_SERVER'] = 'smtp.dreamhost.com'
# os.environ['MAIL_PORT'] = '465'
# os.environ['MAIL_USE_SSL'] = 'True'
# os.environ['MAIL_USERNAME'] = 'chair@therealbackporch.com'
# os.environ['MAIL_PASSWORD'] = '***'
# os.environ['MAIL_DEFAULT_SENDER'] = 'chair@therealbackporch.com'

# Import the Flask app and expose as WSGI application
from app import app as application