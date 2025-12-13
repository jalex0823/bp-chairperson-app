"""Create local test user for quiz testing"""
from app import app, db, User
from datetime import datetime, timedelta

with app.app_context():
    # Create tables if they don't exist
    db.create_all()
    
    # Check if test user exists
    test_user = User.query.filter_by(email='test@test.com').first()
    
    if test_user:
        print("Test user already exists!")
        print(f"Email: {test_user.email}")
        print(f"Name: {test_user.display_name}")
    else:
        # Create test user
        test_user = User(
            display_name='Test User',
            email='test@test.com',
            is_admin=False,
            agreed_guidelines=True,
            sobriety_days=100,
            chair_points=0,
            gender='Other'
        )
        test_user.set_password('test123')
        
        db.session.add(test_user)
        db.session.commit()
        
        print("✓ Test user created successfully!")
        print(f"Email: test@test.com")
        print(f"Password: test123")
        print(f"Name: {test_user.display_name}")
        print(f"BP ID: {test_user.bp_id}")
