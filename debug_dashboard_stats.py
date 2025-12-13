"""Debug script to check dashboard stats."""
from app import app, db, User, Meeting, ChairSignup
from datetime import date, timedelta

with app.app_context():
    # Get Jeff's user account (ID 2)
    user = User.query.get(2)
    
    if not user:
        print("❌ User with ID 2 not found!")
        print("\nAll users:")
        for u in User.query.all():
            print(f"  - {u.display_name} ({u.email}) [ID: {u.id}]")
    else:
        print(f"✅ Found user: {user.display_name} (ID: {user.id})")
        
        # Check for ChairSignups
        signups = ChairSignup.query.filter_by(user_id=user.id).all()
        print(f"\n📋 Total ChairSignups: {len(signups)}")
        
        if signups:
            for signup in signups:
                meeting = Meeting.query.get(signup.meeting_id)
                if meeting:
                    print(f"\n  Meeting ID: {meeting.id}")
                    print(f"  Title: {meeting.title}")
                    print(f"  Date: {meeting.event_date}")
                    print(f"  Time: {meeting.start_time}")
                    print(f"  Is past: {meeting.event_date < date.today()}")
                    print(f"  Is today: {meeting.event_date == date.today()}")
                    print(f"  Is upcoming: {meeting.event_date > date.today()}")
        else:
            print("  No signups found!")
            
        # Check all meetings
        all_meetings = Meeting.query.all()
        print(f"\n📅 Total Meetings in DB: {len(all_meetings)}")
        
        # Check meetings WITH chairs
        meetings_with_chairs = Meeting.query.join(ChairSignup).all()
        print(f"✅ Meetings WITH chairs: {len(meetings_with_chairs)}")
        
        # Check if Jeff is referenced in any ChairSignup at all
        print(f"\n🔍 Direct ChairSignup query for user_id={user.id}:")
        direct_signups = db.session.query(ChairSignup).filter(ChairSignup.user_id == user.id).all()
        print(f"  Found: {len(direct_signups)} signups")
        
        # Show the exact query used in dashboard
        print(f"\n🔍 Dashboard-style query:")
        dashboard_meetings = (
            Meeting.query
            .join(ChairSignup, ChairSignup.meeting_id == Meeting.id)
            .filter(ChairSignup.user_id == user.id)
            .all()
        )
        print(f"  Found: {len(dashboard_meetings)} meetings")
        
        if dashboard_meetings:
            for m in dashboard_meetings:
                print(f"    - {m.title} on {m.event_date}")
