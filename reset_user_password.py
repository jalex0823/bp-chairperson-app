"""Reset password for rblwood@comcast.net"""
from app import app, db, User
from werkzeug.security import generate_password_hash
import secrets
import string

with app.app_context():
    # Find user
    user = User.query.filter_by(email='rblwood@comcast.net').first()
    
    if not user:
        print("❌ User rblwood@comcast.net not found in database")
    else:
        # Generate temporary password
        temp_password = 'BackPorch2025!'
        
        # Update password
        user.password_hash = generate_password_hash(temp_password)
        db.session.commit()
        
        print("="*60)
        print("✅ PASSWORD RESET SUCCESSFUL")
        print("="*60)
        print(f"📧 Email: {user.email}")
        print(f"👤 Display Name: {user.display_name}")
        print(f"🔑 Temporary Password: {temp_password}")
        print("="*60)
        print("\n⚠️  IMPORTANT:")
        print("This reset is for LOCAL database only.")
        print("For PRODUCTION (Heroku), you need to:")
        print("1. Run: heroku run python reset_user_password.py")
        print("2. Or use the admin panel to reset passwords")
        print("="*60)
