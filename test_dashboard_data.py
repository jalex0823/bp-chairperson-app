"""Test dashboard with DreamHost data."""
from app import app, db, User

with app.app_context():
    # Get your user
    user = User.query.filter_by(email="jalex0823@me.com").first()
    
    if user:
        print(f"✅ Found user: {user.display_name}")
        print(f"   Email: {user.email}")
        print(f"   Created: {user.created_at}")
        print(f"   Is Admin: {user.is_admin}")
        
        # Check signups
        from app import ChairSignup, Meeting
        signups = ChairSignup.query.filter_by(user_id=user.id).all()
        print(f"\n📋 Chair Signups: {len(signups)}")
        
        for signup in signups:
            meeting = signup.meeting
            print(f"   - {meeting.title} on {meeting.event_date} at {meeting.start_time}")
            
    else:
        print("❌ User not found with email jalex0823@me.com")
        
        # Show all users
        all_users = User.query.all()
        print(f"\n👥 All users in database:")
        for u in all_users:
            print(f"   - {u.display_name} ({u.email})")
