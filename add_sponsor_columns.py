#!/usr/bin/env python3
"""
Migration script to add missing Sponsor columns (bio/profile_image/etc.)
in a DB-agnostic way (SQLite/MySQL/Postgres).

Why: Heroku Postgres can have an older sponsors table missing these columns.
That causes 500s on /sponsors when SQLAlchemy selects non-existent columns.
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect


def get_database_info():
    """Detect database type and return (db_type, connection_string)."""
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        # Heroku uses postgres:// but SQLAlchemy expects postgresql://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        return "heroku_postgres", database_url

    if os.environ.get("DB_HOST"):
        db_host = os.environ.get("DB_HOST")
        db_name = os.environ.get("DB_NAME")
        db_user = os.environ.get("DB_USER")
        db_password = os.environ.get("DB_PASSWORD")
        db_port = os.environ.get("DB_PORT", "3306")
        connection_string = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        return "mysql", connection_string

    # local fallback (sqlite)
    db_path = os.path.join(os.path.dirname(__file__), "instance", "bp_chair.sqlite3")
    return "sqlite", f"sqlite:///{db_path}"


def _has_column(inspector, table: str, column: str) -> bool:
    try:
        cols = [c["name"] for c in inspector.get_columns(table)]
        return column in cols
    except Exception:
        return False


def add_sponsor_columns():
    db_type, connection_string = get_database_info()
    print(f"Database type: {db_type}")

    engine = create_engine(connection_string)
    inspector = inspect(engine)

    if "sponsors" not in inspector.get_table_names():
        # init-db (db.create_all) should create it; don't fail deploy here.
        print("Sponsors table does not exist yet; skipping sponsor column migration.")
        return True

    # Types:
    # - Postgres: TEXT is unlimited, good for base64 images
    # - SQLite: TEXT is fine
    # - MySQL: TEXT is too small for images; use LONGTEXT
    profile_image_type = "LONGTEXT" if db_type == "mysql" else "TEXT"

    alter_statements = []
    if not _has_column(inspector, "sponsors", "bio"):
        alter_statements.append("ALTER TABLE sponsors ADD COLUMN bio TEXT NULL")
    if not _has_column(inspector, "sponsors", "profile_image"):
        alter_statements.append(f"ALTER TABLE sponsors ADD COLUMN profile_image {profile_image_type} NULL")
    if not _has_column(inspector, "sponsors", "notes"):
        alter_statements.append("ALTER TABLE sponsors ADD COLUMN notes TEXT NULL")
    if not _has_column(inspector, "sponsors", "is_active"):
        # default TRUE keeps existing sponsors visible
        if db_type == "heroku_postgres":
            alter_statements.append("ALTER TABLE sponsors ADD COLUMN is_active BOOLEAN DEFAULT TRUE")
        else:
            alter_statements.append("ALTER TABLE sponsors ADD COLUMN is_active BOOLEAN DEFAULT TRUE")

    if not alter_statements:
        print("OK: sponsors table already has required columns")
        return True

    try:
        with engine.connect() as conn:
            for stmt in alter_statements:
                print(f"Running: {stmt}")
                conn.execute(text(stmt))
            conn.commit()
        print("OK: Successfully applied sponsor column migrations")
        return True
    except Exception as e:
        print(f"ERROR: Error applying sponsor column migrations: {e}")
        return False


if __name__ == "__main__":
    ok = add_sponsor_columns()
    sys.exit(0 if ok else 1)

