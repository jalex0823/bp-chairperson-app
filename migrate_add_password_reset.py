#!/usr/bin/env python
"""Add password_reset_required column to users table"""
import sys
import os

# Ensure app is importable on Heroku
if '/app' not in sys.path:
    sys.path.insert(0, '/app')

from app import app, db
from sqlalchemy import text

print("Starting migration: Add password_reset_required column...")

with app.app_context():
    try:
        # Use text() for raw SQL in SQLAlchemy 2.0+
        with db.engine.connect() as conn:
            # Add column if it doesn't exist
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN password_reset_required BOOLEAN DEFAULT FALSE
            """))
            conn.commit()
            print("✅ Successfully added password_reset_required column!")
    except Exception as e:
        error_msg = str(e).lower()
        if "duplicate column" in error_msg or "already exists" in error_msg:
            print("ℹ️  Column password_reset_required already exists - no action needed")
        else:
            print(f"❌ Error during migration: {e}")
            sys.exit(1)

print("Migration completed!")
