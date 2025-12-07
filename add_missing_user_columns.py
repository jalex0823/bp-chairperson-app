"""
Add missing columns to users table for security features.
Run this script to update the database schema.
"""
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def add_user_security_columns():
    """Add last_login, failed_login_attempts, and locked_until columns to users table."""
    
    # Get database connection details from environment
    db_url = os.getenv('DATABASE_URL')
    
    if db_url:
        # Heroku/Postgres
        print("Using Heroku Postgres database...")
        import psycopg2
        from urllib.parse import urlparse
        
        # Parse the URL
        result = urlparse(db_url)
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        cursor = conn.cursor()
        
        # Check if columns exist
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users'
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        # Add missing columns
        if 'last_login' not in existing_columns:
            print("Adding last_login column...")
            cursor.execute("ALTER TABLE users ADD COLUMN last_login TIMESTAMP NULL")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_last_login ON users(last_login)")
        
        if 'failed_login_attempts' not in existing_columns:
            print("Adding failed_login_attempts column...")
            cursor.execute("ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER DEFAULT 0")
        
        if 'locked_until' not in existing_columns:
            print("Adding locked_until column...")
            cursor.execute("ALTER TABLE users ADD COLUMN locked_until TIMESTAMP NULL")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_locked_until ON users(locked_until)")
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Postgres schema updated successfully!")
        
    else:
        # MySQL/DreamHost
        print("Using MySQL database...")
        import pymysql
        
        db_host = os.getenv("DB_HOST", "mysql.therealbackporch.com")
        db_port = int(os.getenv("DB_PORT", "3306"))
        db_name = os.getenv("DB_NAME", "chairameeting")
        db_user = os.getenv("DB_USER", "chairperson")
        db_password = os.getenv("DB_PASSWORD", "")
        
        conn = pymysql.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name
        )
        cursor = conn.cursor()
        
        # Check if columns exist
        cursor.execute(f"SHOW COLUMNS FROM users")
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        # Add missing columns
        if 'last_login' not in existing_columns:
            print("Adding last_login column...")
            cursor.execute("ALTER TABLE users ADD COLUMN last_login DATETIME NULL")
            cursor.execute("ALTER TABLE users ADD INDEX idx_users_last_login (last_login)")
        
        if 'failed_login_attempts' not in existing_columns:
            print("Adding failed_login_attempts column...")
            cursor.execute("ALTER TABLE users ADD COLUMN failed_login_attempts INT DEFAULT 0")
        
        if 'locked_until' not in existing_columns:
            print("Adding locked_until column...")
            cursor.execute("ALTER TABLE users ADD COLUMN locked_until DATETIME NULL")
            cursor.execute("ALTER TABLE users ADD INDEX idx_users_locked_until (locked_until)")
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ MySQL schema updated successfully!")

if __name__ == "__main__":
    try:
        add_user_security_columns()
    except Exception as e:
        print(f"❌ Error updating schema: {e}")
        import traceback
        traceback.print_exc()
