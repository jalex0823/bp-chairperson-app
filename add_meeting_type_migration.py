#!/usr/bin/env python3
"""
Migration script to add meeting_type column to existing meetings
"""
import os
import sys

# Add the project root to path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

def run_migration():
    """Add meeting_type column to meetings table if it doesn't exist"""
    with app.app_context():
        try:
            # First check if we can connect to the database
            try:
                db.engine.connect().close()
                is_mysql = True
                print("Connected to MySQL database")
            except:
                # If MySQL fails, create a local SQLite database for testing
                app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chairperson_local.db'
                db.create_all()
                is_mysql = False
                print("Using SQLite database for testing")
            
            # Check if column already exists
            if is_mysql:
                result = db.session.execute(text("SELECT COUNT(*) FROM information_schema.columns WHERE table_name='meetings' AND column_name='meeting_type'"))
                column_exists = result.fetchone()[0] > 0
            else:
                result = db.session.execute(text("PRAGMA table_info(meetings)"))
                columns = [row[1] for row in result.fetchall()]
                column_exists = 'meeting_type' in columns
            
            if not column_exists:
                print("Adding meeting_type column to meetings table...")
                
                # Add the column
                if is_mysql:
                    db.session.execute(text("ALTER TABLE meetings ADD COLUMN meeting_type VARCHAR(50) NOT NULL DEFAULT 'Regular'"))
                else:
                    db.session.execute(text("ALTER TABLE meetings ADD COLUMN meeting_type VARCHAR(50) NOT NULL DEFAULT 'Regular'"))
                
                print("✅ Successfully added meeting_type column")
                
                # Update existing meetings to have Regular type
                db.session.execute(text("UPDATE meetings SET meeting_type = 'Regular' WHERE meeting_type IS NULL OR meeting_type = ''"))
                print("✅ Updated all existing meetings to 'Regular' type")
                
                db.session.commit()
                print("✅ Migration completed successfully!")
                
            else:
                print("ℹ️  meeting_type column already exists, skipping migration")
                
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    run_migration()