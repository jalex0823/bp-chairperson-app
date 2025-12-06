import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-in-production")
    # Database configuration
    # Use DATABASE_URL if provided (Heroku), otherwise construct from individual vars
    if os.getenv('DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    else:
        # MySQL (DreamHost) connection details
        DB_HOST = os.environ.get("DB_HOST", "localhost")
        DB_PORT = os.environ.get("DB_PORT", "3306")
        DB_NAME = os.environ.get("DB_NAME", "chairameeting")
        DB_USER = os.environ.get("DB_USER", "chairperson")
        DB_PASSWORD = os.environ.get("DB_PASSWORD", "12!Gratitudeee")

        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
        )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email configuration for DreamHost
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.dreamhost.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 465))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "False").lower() == "true"
    MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL", "True").lower() == "true"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "noreply@backporchmeetings.org")

    # Scheduler configuration
    SCHEDULER_API_ENABLED = True
