"""
Quick migration to add password_reset_required column
Run directly via: heroku run python -c "exec(open('quick_migration.py').read())"
Or simply: python quick_migration.py
"""
import os
import sys

# Add the app directory to path for Heroku
sys.path.insert(0, '/app')

from app import app, db

print("Starting migration...")

with app.app_context():
    try:
        with db.engine.begin() as conn:
            # Try to add the column
            conn.execute(db.text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS password_reset_required BOOLEAN DEFAULT FALSE
            """))
            print("✅ Migration successful! Added password_reset_required column")
    except Exception as e:
        if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
            print("ℹ️  Column already exists - no action needed")
        else:
            print(f"❌ Migration error: {e}")
            raise
