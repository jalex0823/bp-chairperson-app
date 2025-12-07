#!/usr/bin/env python3
"""
Create admin user in the database.
"""

import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime

# SQLite database path
DB_PATH = 'instance/bp_chair.sqlite3'

def create_admin_user():
    """Create admin user with specified credentials."""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # User details
    display_name = 'jalex0823'
    email = 'jalex0823@admin.local'
    password = 'Disneychannel911!'
    password_hash = generate_password_hash(password)
    
    # Check if user already exists
    cursor.execute("SELECT id FROM users WHERE display_name = ?", (display_name,))
    existing = cursor.fetchone()
    
    if existing:
        # Update existing user to be admin
        cursor.execute("""
            UPDATE users 
            SET password_hash = ?, is_admin = 1, email = ?
            WHERE display_name = ?
        """, (password_hash, email, display_name))
        print(f"✓ Updated existing user '{display_name}' to admin with new password")
    else:
        # Create new admin user
        cursor.execute("""
            INSERT INTO users (display_name, email, password_hash, is_admin, 
                             sobriety_days, agreed_guidelines, created_at, gender,
                             failed_login_attempts)
            VALUES (?, ?, ?, 1, 0, 1, ?, 'male', 0)
        """, (display_name, email, password_hash, datetime.utcnow()))
        print(f"✓ Created new admin user '{display_name}'")
    
    conn.commit()
    conn.close()
    
    print(f"\nAdmin credentials:")
    print(f"  Display Name: {display_name}")
    print(f"  Password: {password}")
    print(f"  Email: {email}")
    print(f"  Admin: Yes")

if __name__ == '__main__':
    try:
        create_admin_user()
        print("\n✓ Admin user created successfully!")
    except Exception as e:
        print(f"\n❌ Failed to create admin user: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
