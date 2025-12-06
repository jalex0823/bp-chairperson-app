"""
DreamHost cron worker to run scheduled jobs.

Usage: configure a cron entry to run this script periodically (e.g., hourly) to send open slot reminders.
You can extend it to run other maintenance tasks.
"""
from datetime import datetime
from app import app
from app import send_open_slot_reminder

def main():
    with app.app_context():
        # Example: run weekly open slot reminder when it's Sunday 10:00 (server time)
        now = datetime.now()
        if now.weekday() == 6 and now.hour == 10:  # Sunday at 10am
            send_open_slot_reminder()

if __name__ == "__main__":
    main()