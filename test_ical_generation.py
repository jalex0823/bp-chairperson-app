"""Test script to verify iCal generation and email functionality."""
from app import app, db, Meeting, ChairSignup, User, generate_meeting_ical
from datetime import datetime, date, time

with app.app_context():
    # Get a sample meeting and user
    meeting = Meeting.query.first()
    user = User.query.filter_by(id=2).first()  # Your account
    
    if meeting and user:
        print(f"✅ Testing with meeting: {meeting.title}")
        print(f"   Date: {meeting.event_date}")
        print(f"   Time: {meeting.start_time}")
        print(f"   User: {user.display_name}")
        
        # Generate iCal
        try:
            ical_data = generate_meeting_ical(meeting, user.display_name)
            print(f"\n✅ iCal generated successfully!")
            print(f"   Size: {len(ical_data)} bytes")
            
            # Save to file for testing
            with open('test_meeting.ics', 'wb') as f:
                f.write(ical_data)
            print(f"\n✅ Saved to test_meeting.ics")
            print(f"   You can open this file to verify the calendar event works")
            
            # Show first 500 chars of iCal
            print(f"\n📄 iCal Preview:")
            print("=" * 60)
            print(ical_data.decode('utf-8')[:500])
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Error generating iCal: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ No meeting or user found to test with")
        if not meeting:
            print("   No meetings in database")
        if not user:
            print("   User with ID 2 not found")
