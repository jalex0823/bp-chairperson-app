"""
Remove all ChairSignup records for 'Jeff The Genius' on Sunday meetings.
DRY RUN first — prints what would be deleted, then prompts to confirm.
"""
from app import app, db, User, ChairSignup, Meeting

with app.app_context():
    # Find the user
    user = User.query.filter(User.display_name.ilike('%Jeff%Genius%')).first()
    if not user:
        print("ERROR: Could not find user matching 'Jeff The Genius'")
        exit(1)

    print(f"Found user: {user.display_name} (ID={user.id}, {user.email})")

    # Find all their signups on Sunday meetings
    signups = (
        db.session.query(ChairSignup)
        .join(Meeting)
        .filter(ChairSignup.user_id == user.id)
        .all()
    )

    sunday_signups = [s for s in signups if s.meeting.event_date.weekday() == 6]

    if not sunday_signups:
        print("No Sunday signups found for this user.")
        exit(0)

    print(f"\nFound {len(sunday_signups)} Sunday signup(s) to remove:")
    for s in sunday_signups:
        print(f"  - Meeting ID {s.meeting_id} | {s.meeting.event_date} | {s.meeting.title}")

    confirm = input("\nType YES to delete these signups: ").strip()
    if confirm != "YES":
        print("Aborted.")
        exit(0)

    for s in sunday_signups:
        db.session.delete(s)
    db.session.commit()
    print(f"\nDone. Removed {len(sunday_signups)} Sunday signup(s) for {user.display_name}.")
