"""Minimal Flask app to test Heroku deployment"""
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello from Heroku! If you see this, Flask is working."

@app.route('/test-config')
def test_config():
    import os
    config_info = {
        'DB_HOST': os.getenv('DB_HOST', 'NOT SET'),
        'DB_NAME': os.getenv('DB_NAME', 'NOT SET'),
        'DB_USER': os.getenv('DB_USER', 'NOT SET'),
        'DB_PASSWORD': '***' if os.getenv('DB_PASSWORD') else 'NOT SET',
        'MAIL_USERNAME': os.getenv('MAIL_USERNAME', 'NOT SET'),
        'MAIL_PASSWORD': '***' if os.getenv('MAIL_PASSWORD') else 'NOT SET',
        'SECRET_KEY': '***' if os.getenv('SECRET_KEY') else 'NOT SET',
    }
    return f"<pre>{config_info}</pre>"

if __name__ == '__main__':
    app.run()
