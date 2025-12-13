#!/usr/bin/env python3
"""Create admin account directly"""
from app import app, db, User
from werkzeug.security import generate_password_hash
from datetime import datetime

with app.app_context():
    # Create admin user
    email = 'jeff@backporch.com'
    
    # Check if exists
    existing = User.query.filter_by(email=email).first()
    
    if existing:
        print(f"User {email} already exists!")
        print(f"Making them admin...")
        existing.is_admin = True
        existing.password_hash = generate_password_hash('admin123')
        db.session.commit()
        print(f"\n✅ Updated user to admin")
    else:
        user = User(
            email=email,
            display_name='Jeff Alexander',
            password_hash=generate_password_hash('admin123'),
            is_admin=True,
            agreed_guidelines=True
        )
        db.session.add(user)
        db.session.commit()
        print(f"\n✅ Created new admin user")
    
    print("\n" + "="*60)
    print("ADMIN LOGIN CREDENTIALS")
    print("="*60)
    print(f"📧 Email: {email}")
    print(f"🔑 Password: admin123")
    print(f"🌐 Login URL: http://127.0.0.1:5000/login")
    print("="*60)
