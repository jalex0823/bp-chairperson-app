#!/usr/bin/env python3
"""Check existing users and reset admin password"""
from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    print("\n" + "="*60)
    print("EXISTING USERS IN DATABASE:")
    print("="*60)
    
    users = User.query.all()
    
    if not users:
        print("❌ No users found in database!")
    else:
        for user in users:
            print(f"\n👤 User ID: {user.id}")
            print(f"   Email: {user.email or 'N/A'}")
            print(f"   Username: {user.username or 'N/A'}")
            print(f"   Display Name: {user.display_name or 'N/A'}")
            print(f"   BP ID: {user.bp_id or 'N/A'}")
            print(f"   Is Admin: {'✓ YES' if user.is_admin else '✗ No'}")
    
    print("\n" + "="*60)
    print("RESETTING ADMIN PASSWORD")
    print("="*60)
    
    # Find admin user (check multiple possibilities)
    admin = User.query.filter_by(is_admin=True).first()
    
    if not admin:
        # Try to find by email
        for email in ['jalex0823@admin.local', 'admin@backporch.com', 'jalex0823@gmail.com']:
            admin = User.query.filter_by(email=email).first()
            if admin:
                break
    
    if not admin:
        # Try to find by BP ID
        admin = User.query.filter_by(bp_id='BP-1002').first()
    
    if admin:
        # Reset password
        new_password = 'admin123'
        admin.password_hash = generate_password_hash(new_password)
        admin.is_admin = True  # Ensure admin flag is set
        db.session.commit()
        
        print(f"\n✅ Admin password reset successfully!")
        print(f"\n📧 Email: {admin.email or 'N/A'}")
        print(f"👤 Username: {admin.username or 'N/A'}")
        print(f"🔑 New Password: {new_password}")
        print(f"🌐 Login URL: http://127.0.0.1:5000/login")
    else:
        print("\n❌ No admin user found!")
        print("Creating new admin user...")
        
        new_admin = User(
            username='admin',
            email='admin@backporch.com',
            display_name='Administrator',
            bp_id='BP-ADMIN',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(new_admin)
        db.session.commit()
        
        print(f"\n✅ New admin user created!")
        print(f"\n📧 Email: admin@backporch.com")
        print(f"👤 Username: admin")
        print(f"🔑 Password: admin123")
        print(f"🌐 Login URL: http://127.0.0.1:5000/login")
    
    print("="*60 + "\n")
