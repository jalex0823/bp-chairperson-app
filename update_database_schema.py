#!/usr/bin/env python3
"""
Add ChairpersonAvailability table to existing database
"""
import os
import sys
from dotenv import load_dotenv

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from app import app, db, ChairpersonAvailability

def update_database():
    """Add the new ChairpersonAvailability table to the database."""
    with app.app_context():
        try:
            # Force SQLite for development/testing
            if 'mysql' in app.config.get('SQLALCHEMY_DATABASE_URI', ''):
                print("MySQL detected, switching to SQLite for development...")
                import tempfile
                import uuid
                test_db_path = os.path.join(tempfile.gettempdir(), f'bp_dev_{uuid.uuid4().hex[:8]}.db')
                app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{test_db_path}'
                print(f"Using SQLite database: {test_db_path}")
            
            # Check if table already exists
            try:
                inspector = db.inspect(db.engine)
                existing_tables = inspector.get_table_names()
            except:
                existing_tables = []
            
            if 'chairperson_availability' not in existing_tables:
                print("Creating chairperson_availability table...")
                db.create_all()
                print("✅ Table created successfully!")
            else:
                print("✅ Table already exists!")
                
        except Exception as e:
            print(f"❌ Error updating database: {e}")
            return False
            
    return True

if __name__ == "__main__":
    print("=== DATABASE UPDATE ===")
    print("Adding ChairpersonAvailability table...")
    
    success = update_database()
    
    if success:
        print("\n🎉 Database update complete!")
        print("Users can now volunteer for chairperson duties on any date.")
    else:
        print("\n💥 Database update failed!")
        sys.exit(1)