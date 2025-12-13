"""
Migration script to add chair_points column to users table.
Run this script to add the ChairPoints feature to existing databases.

Usage:
    python add_chair_points_migration.py
"""

from app import app, db
from sqlalchemy import text

def add_chair_points_column():
    """Add chair_points column to users table if it doesn't exist."""
    with app.app_context():
        inspector = db.inspect(db.engine)
        
        # Check if users table exists
        if 'users' not in inspector.get_table_names():
            print("❌ Users table not found!")
            return False
        
        # Check if chair_points column already exists
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        if 'chair_points' in columns:
            print("✅ chair_points column already exists!")
            return True
        
        # Add the column
        try:
            with db.engine.connect() as conn:
                # For PostgreSQL and MySQL
                conn.execute(text(
                    "ALTER TABLE users ADD COLUMN chair_points INTEGER DEFAULT 0"
                ))
                conn.commit()
                
                # Create index for performance
                conn.execute(text(
                    "CREATE INDEX ix_users_chair_points ON users(chair_points)"
                ))
                conn.commit()
                
            print("✅ Successfully added chair_points column and index!")
            return True
            
        except Exception as e:
            print(f"❌ Error adding chair_points column: {e}")
            return False


def backfill_chair_points():
    """Backfill chair_points for existing users based on their completed meetings."""
    from app import User, Meeting, ChairSignup
    from datetime import date
    
    with app.app_context():
        try:
            # Find all users who have chaired meetings in the past
            users_with_signups = db.session.query(User).join(ChairSignup).distinct().all()
            
            updated_count = 0
            total_points = 0
            
            for user in users_with_signups:
                # Count completed meetings (past meetings only)
                completed_meetings = db.session.query(ChairSignup).join(Meeting).filter(
                    ChairSignup.user_id == user.id,
                    Meeting.event_date < date.today()
                ).count()
                
                if completed_meetings > 0:
                    user.chair_points = completed_meetings
                    updated_count += 1
                    total_points += completed_meetings
                    print(f"  ✓ {user.display_name} (BP-{1000 + user.id}): {completed_meetings} ChairPoints")
            
            db.session.commit()
            print(f"\n✅ Backfilled ChairPoints for {updated_count} users (Total: {total_points} points)")
            return True
            
        except Exception as e:
            print(f"❌ Error backfilling chair_points: {e}")
            db.session.rollback()
            return False


if __name__ == '__main__':
    print("=" * 60)
    print("ChairPoints Migration Script")
    print("=" * 60)
    print()
    
    print("Step 1: Adding chair_points column...")
    if add_chair_points_column():
        print()
        print("Step 2: Backfilling ChairPoints from historical data...")
        backfill_chair_points()
        print()
        print("=" * 60)
        print("✅ Migration complete!")
        print("=" * 60)
    else:
        print()
        print("=" * 60)
        print("❌ Migration failed!")
        print("=" * 60)
