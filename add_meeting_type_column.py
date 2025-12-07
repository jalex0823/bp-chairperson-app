#!/usr/bin/env python3
"""
Migration script to add meeting_type column to meetings table.
This ensures local SQLite database matches the model definition.
"""

import os
import sqlite3
import pymysql
from urllib.parse import urlparse

def get_database_info():
    """Determine database type from DATABASE_URL."""
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///instance/bp_chair.sqlite3')
    
    if database_url.startswith('sqlite'):
        db_path = database_url.replace('sqlite:///', '')
        return 'sqlite', db_path
    elif database_url.startswith('postgres'):
        return 'postgres', database_url
    elif database_url.startswith('mysql'):
        return 'mysql', database_url
    else:
        return 'unknown', database_url

def migrate_sqlite(db_path):
    """Add meeting_type column to SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if column exists
    cursor.execute("PRAGMA table_info(meetings)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'meeting_type' not in columns:
        print("Adding meeting_type column to meetings table...")
        
        # Add the column with default value
        cursor.execute("""
            ALTER TABLE meetings 
            ADD COLUMN meeting_type VARCHAR(50) NOT NULL DEFAULT 'Regular'
        """)
        
        # Create index for filtering
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_meetings_meeting_type 
            ON meetings(meeting_type)
        """)
        
        conn.commit()
        print("✓ Successfully added meeting_type column to meetings table")
    else:
        print("✓ meeting_type column already exists in meetings table")
    
    conn.close()

def migrate_mysql(database_url):
    """Add meeting_type column to MySQL database."""
    parsed = urlparse(database_url)
    
    conn = pymysql.connect(
        host=parsed.hostname,
        user=parsed.username,
        password=parsed.password,
        database=parsed.path[1:],  # Remove leading /
        port=parsed.port or 3306
    )
    
    cursor = conn.cursor()
    
    # Check if column exists
    cursor.execute("""
        SELECT COUNT(*) 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME = 'meetings'
        AND COLUMN_NAME = 'meeting_type'
    """)
    
    exists = cursor.fetchone()[0] > 0
    
    if not exists:
        print("Adding meeting_type column to meetings table...")
        
        # Add the column with default value
        cursor.execute("""
            ALTER TABLE meetings 
            ADD COLUMN meeting_type VARCHAR(50) NOT NULL DEFAULT 'Regular'
        """)
        
        # Create index for filtering
        cursor.execute("""
            CREATE INDEX idx_meetings_meeting_type 
            ON meetings(meeting_type)
        """)
        
        conn.commit()
        print("✓ Successfully added meeting_type column to meetings table")
    else:
        print("✓ meeting_type column already exists in meetings table")
    
    conn.close()

def migrate_postgres(database_url):
    """Add meeting_type column to PostgreSQL database."""
    # Heroku DATABASE_URL uses 'postgres://' but psycopg2 expects 'postgresql://'
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    import psycopg2
    
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    # Check if column exists
    cursor.execute("""
        SELECT COUNT(*) 
        FROM information_schema.columns 
        WHERE table_name = 'meetings'
        AND column_name = 'meeting_type'
    """)
    
    exists = cursor.fetchone()[0] > 0
    
    if not exists:
        print("Adding meeting_type column to meetings table...")
        
        # Add the column with default value
        cursor.execute("""
            ALTER TABLE meetings 
            ADD COLUMN meeting_type VARCHAR(50) NOT NULL DEFAULT 'Regular'
        """)
        
        # Create index for filtering
        cursor.execute("""
            CREATE INDEX idx_meetings_meeting_type 
            ON meetings(meeting_type)
        """)
        
        conn.commit()
        print("✓ Successfully added meeting_type column to meetings table")
    else:
        print("✓ meeting_type column already exists in meetings table")
    
    conn.close()

if __name__ == '__main__':
    db_type, db_info = get_database_info()
    
    print(f"Database type: {db_type}")
    
    try:
        if db_type == 'sqlite':
            migrate_sqlite(db_info)
        elif db_type == 'mysql':
            migrate_mysql(db_info)
        elif db_type == 'postgres':
            migrate_postgres(db_info)
        else:
            print(f"Unknown database type: {db_type}")
            exit(1)
        
        print("\n✓ Migration completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
