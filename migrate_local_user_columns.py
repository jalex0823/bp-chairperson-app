#!/usr/bin/env python3
"""
Add missing security columns to users table in SQLite database.
This is a local-only migration script.
"""

import sqlite3
import os

# SQLite database path
DB_PATH = 'instance/bp_chair.sqlite3'

def migrate_sqlite():
    """Add security columns to SQLite users table."""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database file not found: {DB_PATH}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if columns exist
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    
    columns_to_add = {
        'last_login': "ALTER TABLE users ADD COLUMN last_login DATETIME NULL",
        'failed_login_attempts': "ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER NOT NULL DEFAULT 0",
        'locked_until': "ALTER TABLE users ADD COLUMN locked_until DATETIME NULL"
    }
    
    added = []
    for col_name, sql in columns_to_add.items():
        if col_name not in columns:
            print(f"Adding {col_name} column...")
            cursor.execute(sql)
            added.append(col_name)
        else:
            print(f"✓ {col_name} column already exists")
    
    if added:
        # Create indexes
        indexes = {
            'idx_users_last_login': "CREATE INDEX IF NOT EXISTS idx_users_last_login ON users(last_login)",
            'idx_users_locked_until': "CREATE INDEX IF NOT EXISTS idx_users_locked_until ON users(locked_until)"
        }
        
        for idx_name, sql in indexes.items():
            print(f"Creating index {idx_name}...")
            cursor.execute(sql)
        
        conn.commit()
        print(f"\n✓ Successfully added {len(added)} column(s) to users table")
    else:
        print("\n✓ All columns already exist in users table")
    
    conn.close()
    return True

if __name__ == '__main__':
    try:
        if migrate_sqlite():
            print("\n✓ Migration completed successfully!")
        else:
            print("\n❌ Migration failed!")
            exit(1)
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
