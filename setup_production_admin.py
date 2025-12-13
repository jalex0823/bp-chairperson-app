"""
Production Admin Account Setup Script
Run this on Heroku to create/update admin account in production database
"""
from app import app, db, User
from werkzeug.security import generate_password_hash

def setup_production_admin():
    with app.app_context():
        email = 'jalex0823@me.com'
        password = 'Disnerychannel911!'
        
        # Find or create admin user
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Update existing user
            user.is_admin = True
            user.password_hash = generate_password_hash(password)
            print(f"✅ Updated existing user: {email}")
        else:
            # Create new admin user
            user = User(
                email=email,
                display_name='jalex0823',
                password_hash=generate_password_hash(password),
                is_admin=True,
                chair_points=0
            )
            db.session.add(user)
            print(f"✅ Created new admin user: {email}")
        
        db.session.commit()
        
        print("\n" + "="*60)
        print("🎉 PRODUCTION ADMIN CREDENTIALS")
        print("="*60)
        print(f"📧 Email: {email}")
        print(f"🔑 Password: {password}")
        print(f"🌐 URL: https://backporch-chair-app-35851db28c9c.herokuapp.com/login")
        print("="*60)
        
        return True

if __name__ == '__main__':
    setup_production_admin()
