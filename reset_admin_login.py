"""Reset admin password and test login"""
from app import app, db, User
from werkzeug.security import generate_password_hash, check_password_hash

with app.app_context():
    # Find admin user
    admin = User.query.filter_by(email='jalex0823@admin.local').first()
    
    if not admin:
        print("❌ Admin user not found!")
    else:
        # Set password to 'admin123'
        new_password = 'admin123'
        admin.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        print("✅ Admin password reset successfully!")
        print(f"📧 Email: {admin.email}")
        print(f"🔑 Password: {new_password}")
        print(f"👤 Display Name: {admin.display_name}")
        print(f"🔐 Is Admin: {admin.is_admin}")
        
        # Verify password works
        if check_password_hash(admin.password_hash, new_password):
            print("✅ Password verification: SUCCESS")
        else:
            print("❌ Password verification: FAILED")
        
        # Check if email is verified
        print(f"📧 Email Verified: {admin.email_verified}")
