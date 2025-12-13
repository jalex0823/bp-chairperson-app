#!/usr/bin/env python3
"""
Database setup and testing script for registration system.
"""
import os
from dotenv import load_dotenv

load_dotenv()

def test_database_setup():
    """Test database setup with different configurations."""
    print("=== Database Setup Test ===")
    
    # Test with SQLite (local)
    print("\n1. Testing with SQLite (local)...")
    os.environ['DATABASE_URL'] = 'sqlite:///bp_test.db'
    
    try:
        from app import app, db, User
        
        with app.app_context():
            # Create tables
            db.drop_all()  # Clean start
            db.create_all()
            
            # Test user creation
            test_user = User(
                display_name="Test Chair",
                email="test@backporch.org",
                is_admin=False,
                sobriety_days=365,
                agreed_guidelines=True,
                gender="male"
            )
            test_user.set_password("testpass123")
            
            db.session.add(test_user)
            db.session.commit()
            
            # Verify user was saved
            saved_user = User.query.filter_by(email="test@backporch.org").first()
            if saved_user:
                print(f"✅ SQLite test passed - User ID: {saved_user.id}, BP ID: {saved_user.bp_id}")
                
                # Clean up
                db.session.delete(saved_user)
                db.session.commit()
                return True
            else:
                print("❌ SQLite test failed - User not found")
                return False
                
    except Exception as e:
        print(f"❌ SQLite test failed: {e}")
        return False
    finally:
        # Clean up test database
        try:
            if os.path.exists('bp_test.db'):
                os.remove('bp_test.db')
        except:
            pass

def check_mysql_config():
    """Check MySQL configuration without connecting."""
    print("\n2. Checking MySQL configuration...")
    
    db_host = os.environ.get("DB_HOST")
    db_name = os.environ.get("DB_NAME") 
    db_user = os.environ.get("DB_USER")
    db_password = os.environ.get("DB_PASSWORD", "")
    
    print(f"   Host: {db_host}")
    print(f"   Database: {db_name}")
    print(f"   User: {db_user}")
    print(f"   Password: {'[SET]' if db_password else '[EMPTY]'}")
    
    if not db_password:
        print("   ⚠️  Warning: No MySQL password set in DB_PASSWORD environment variable")
        return False
    
    return True

def create_init_sql():
    """Create SQL initialization script for MySQL."""
    print("\n3. Creating MySQL initialization script...")
    
    init_sql = """-- BP Chairperson App Database Initialization
-- Run this script in your MySQL database to create tables

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    display_name VARCHAR(80) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    sobriety_days INT DEFAULT NULL,
    agreed_guidelines BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    gender VARCHAR(10) DEFAULT NULL
);

-- Create meetings table
CREATE TABLE IF NOT EXISTS meetings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    zoom_link VARCHAR(500),
    event_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME,
    is_open BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    gender_restriction VARCHAR(10) DEFAULT NULL
);

-- Create chair_signups table
CREATE TABLE IF NOT EXISTS chair_signups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    meeting_id INT UNIQUE NOT NULL,
    user_id INT NOT NULL,
    display_name_snapshot VARCHAR(80) NOT NULL,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (meeting_id) REFERENCES meetings(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_meetings_date ON meetings(event_date);
CREATE INDEX IF NOT EXISTS idx_meetings_date_time ON meetings(event_date, start_time);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_chair_signups_meeting ON chair_signups(meeting_id);
CREATE INDEX IF NOT EXISTS idx_chair_signups_user ON chair_signups(user_id);

-- Insert admin user (change password!)
INSERT IGNORE INTO users (display_name, email, password_hash, is_admin, agreed_guidelines)
VALUES ('Admin', 'admin@backporch.org', 'scrypt:32768:8:1$changethis$changethishashinproduction', TRUE, TRUE);

SELECT 'Database initialization complete!' as status;
"""
    
    try:
        with open('init_database.sql', 'w') as f:
            f.write(init_sql)
        print("✅ Created init_database.sql")
        print("   Run this script in your MySQL database to set up tables")
        return True
    except Exception as e:
        print(f"❌ Failed to create SQL script: {e}")
        return False

if __name__ == "__main__":
    print("=== Database Setup for BP Chairperson App ===")
    
    sqlite_ok = test_database_setup()
    mysql_config_ok = check_mysql_config()
    sql_script_ok = create_init_sql()
    
    print("\n=== Summary ===")
    print(f"SQLite Test: {'✅' if sqlite_ok else '❌'}")
    print(f"MySQL Config: {'✅' if mysql_config_ok else '❌'}")
    print(f"SQL Script: {'✅' if sql_script_ok else '❌'}")
    
    if sqlite_ok:
        print("\n✅ Registration system works with local database")
    
    if not mysql_config_ok:
        print("\n⚠️  To use MySQL, set DB_PASSWORD in your .env file")
        print("   Contact your database administrator for the password")
    
    print("\n📁 Files created:")
    if os.path.exists('init_database.sql'):
        print("   - init_database.sql (run this in MySQL)")