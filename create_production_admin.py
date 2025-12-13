#!/usr/bin/env python3
"""
Create admin user in production database (works with both MySQL and PostgreSQL).
This script uses the same database connection as the app.
"""

import os
import sys
from app import app, db, User

def create_production_admin():
    """Create or update admin user in production database."""
    
    with app.app_context():
        # Admin credentials
        display_name = 'jalex0823'
        email = 'jalex0823@admin.local'
        password = 'Disneychannel911!'
        
        print(f"Checking database connection...")
        print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
        
        # Check if user already exists
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Update existing user
            user.display_name = display_name
            user.set_password(password)
            user.is_admin = True
            user.agreed_guidelines = True
            user.failed_login_attempts = 0
            user.locked_until = None
            print(f"✓ Updated existing user '{display_name}' to admin")
        else:
            # Create new admin user
            user = User(
                display_name=display_name,
                email=email,
                is_admin=True,
                agreed_guidelines=True,
                sobriety_days=0,
                gender='male',
                failed_login_attempts=0
            )
            user.set_password(password)
            db.session.add(user)
            print(f"✓ Created new admin user '{display_name}'")
        
        db.session.commit()
        
        print(f"\n{'='*50}")
        print(f"Admin User Successfully Created/Updated!")
        print(f"{'='*50}")
        print(f"Display Name: {display_name}")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"Admin: Yes")
        print(f"{'='*50}\n")

if __name__ == '__main__':
    try:
        create_production_admin()
        print("✓ Operation completed successfully!")
    except Exception as e:
        print(f"\n❌ Failed to create admin user: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
