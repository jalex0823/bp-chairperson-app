import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-in-production")
    # Database configuration
    # Use DATABASE_URL if provided (Heroku), otherwise construct from individual vars
    if os.getenv('DATABASE_URL'):
        raw_url = os.environ.get("DATABASE_URL")
        # Normalize Heroku Postgres URLs and set driver explicitly
        # Heroku may provide postgres://; SQLAlchemy expects postgresql+psycopg2://
        if raw_url.startswith("postgres://"):
            raw_url = raw_url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif raw_url.startswith("postgresql://"):
            raw_url = raw_url.replace("postgresql://", "postgresql+psycopg2://", 1)
        SQLALCHEMY_DATABASE_URI = raw_url
    else:
        # MySQL (DreamHost) connection details
        DB_HOST = os.environ.get("DB_HOST", "mysql.therealbackporch.com")
        DB_PORT = os.environ.get("DB_PORT", "3306")
        DB_NAME = os.environ.get("DB_NAME", "chairameeting")
        DB_USER = os.environ.get("DB_USER", "chairperson")
        # Do not hard-code passwords; require via environment
        DB_PASSWORD = os.environ.get("DB_PASSWORD", "")

        # URL-encode user and password to safely handle special characters (e.g., ! @ : / ? #)
        from urllib.parse import quote_plus
        enc_user = quote_plus(DB_USER)
        enc_password = quote_plus(DB_PASSWORD)

        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{enc_user}:{enc_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
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

    # Registration gating
    REGISTRATION_ENABLED = os.environ.get("REGISTRATION_ENABLED", "True").lower() == "true"
    # Default a placeholder unlock key so the registration form is gated by default.
    # Override in environment for production.
    REGISTRATION_ACCESS_CODE = os.environ.get("REGISTRATION_ACCESS_CODE", "BACKPORCH-KEY")
    # Optional: comma-separated list of codes (overrides single code if provided)
    REGISTRATION_ACCESS_CODES = os.environ.get("REGISTRATION_ACCESS_CODES")
