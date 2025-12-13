#!/usr/bin/env python3
"""
Enhanced background worker for chairperson reminder emails and other scheduled tasks.
This script should be run periodically (every hour) via cron or similar scheduler.
"""
import os
import sys
from datetime import datetime, timedelta
import time

# Add the project root to path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db, check_and_send_reminders, send_meeting_confirmations
except ImportError as e:
    print(f"❌ Failed to import app components: {e}")
    sys.exit(1)

def run_scheduled_tasks():
    """Run all scheduled tasks"""
    with app.app_context():
        try:
            print(f"🕐 Starting scheduled tasks at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Send reminder emails
            reminder_count = check_and_send_reminders()
            print(f"📧 Sent {reminder_count} reminder emails")
            
            # Send confirmation emails for recent signups
            confirmation_count = send_meeting_confirmations()
            print(f"✅ Sent {confirmation_count} confirmation emails")
            
            # Log activity
            total_emails = reminder_count + confirmation_count
            if total_emails > 0:
                print(f"✅ Completed: {total_emails} total emails sent")
            else:
                print("ℹ️  No emails needed at this time")
                
        except Exception as e:
            print(f"❌ Error in scheduled tasks: {e}")
            import traceback
            traceback.print_exc()


def run_continuous_mode():
    """Run continuously with hourly checks (for testing/development)"""
    print("🔄 Running in continuous mode - checking every hour")
    print("   Use Ctrl+C to stop")
    
    try:
        while True:
            run_scheduled_tasks()
            print(f"😴 Sleeping for 1 hour...")
            time.sleep(3600)  # Sleep for 1 hour
    except KeyboardInterrupt:
        print("\n👋 Continuous mode stopped")


def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        run_continuous_mode()
    else:
        run_scheduled_tasks()


if __name__ == "__main__":
    main()