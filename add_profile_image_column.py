#!/usr/bin/env python3
"""
Migration script to add profile_image column to users table.
"""
import os
import sys
from sqlalchemy import create_engine, text, inspect

def get_database_info():
    """Detect database type and return connection string."""
    # Check for Heroku-style DATABASE_URL first
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Heroku uses postgres:// but SQLAlchemy 1.4+ requires postgresql://
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        return 'heroku_postgres', database_url
    
    # Check for individual MySQL env vars (DreamHost style)
    if os.environ.get('DB_HOST'):
        db_host = os.environ.get('DB_HOST')
        db_name = os.environ.get('DB_NAME')
        db_user = os.environ.get('DB_USER')
        db_password = os.environ.get('DB_PASSWORD')
        db_port = os.environ.get('DB_PORT', '3306')
        
        connection_string = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        return 'mysql', connection_string
    
    # Default to SQLite for local development
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'bp_chair.sqlite3')
    return 'sqlite', f'sqlite:///{db_path}'

def add_profile_image_column():
    """Add profile_image column to users table if it doesn't exist."""
    db_type, connection_string = get_database_info()
    
    print(f"Database type: {db_type}")
    print(f"Connection string: {connection_string[:50]}...")
    
    engine = create_engine(connection_string)
    
    # Check if column already exists
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'profile_image' in columns:
        print("✓ Column 'profile_image' already exists in users table")
        return True
    
    print("Adding profile_image column to users table...")
    
    try:
        with engine.connect() as conn:
            if db_type == 'sqlite':
                conn.execute(text("""
                    ALTER TABLE users ADD COLUMN profile_image VARCHAR(255)
                """))
            elif db_type == 'mysql':
                conn.execute(text("""
                    ALTER TABLE users ADD COLUMN profile_image VARCHAR(255) DEFAULT NULL
                """))
            else:  # PostgreSQL
                conn.execute(text("""
                    ALTER TABLE users ADD COLUMN profile_image VARCHAR(255)
                """))
            
            conn.commit()
            print("✓ Successfully added profile_image column")
            return True
            
    except Exception as e:
        print(f"✗ Error adding profile_image column: {e}")
        return False

if __name__ == '__main__':
    success = add_profile_image_column()
    sys.exit(0 if success else 1)
