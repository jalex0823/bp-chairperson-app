"""Test DreamHost MySQL connection."""
from app import app, db, User, Meeting, ChairSignup
from sqlalchemy import text

with app.app_context():
    try:
        # Test basic connection
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"📊 Database URI: {db_uri[:60]}...")
        
        # Test query
        result = db.session.execute(text("SELECT 1")).scalar()
        print(f"✅ Database connection successful! (test query result: {result})")
        
        # Count users
        user_count = User.query.count()
        print(f"👥 Total users in database: {user_count}")
        
        # Count meetings
        meeting_count = Meeting.query.count()
        print(f"📅 Total meetings in database: {meeting_count}")
        
        # Count signups
        signup_count = ChairSignup.query.count()
        print(f"✍️  Total chair signups: {signup_count}")
        
        # Show recent users
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        print(f"\n👤 Recent users:")
        for user in recent_users:
            print(f"   - {user.display_name} ({user.email}) - Created: {user.created_at}")
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        import traceback
        traceback.print_exc()
