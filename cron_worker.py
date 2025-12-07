"""
DreamHost cron worker to run scheduled jobs.

Usage: configure a cron entry to run this script periodically (e.g., hourly) to send open slot reminders.
You can extend it to run other maintenance tasks.
"""
from datetime import datetime
from app import app
from app import send_open_slot_reminder, import_meetings_from_ics, SOURCE_MEETINGS_ICS_URL
from app import import_meetings_from_webpage, SOURCE_MEETINGS_WEB_URL

def main():
    with app.app_context():
        # Example: run weekly open slot reminder when it's Sunday 10:00 (server time)
        now = datetime.now()
        if now.weekday() == 6 and now.hour == 10:  # Sunday at 10am
            send_open_slot_reminder()
        # Nightly sync of meetings from external ICS at 03:00
        if SOURCE_MEETINGS_ICS_URL and now.hour == 3:
            try:
                count = import_meetings_from_ics(SOURCE_MEETINGS_ICS_URL, replace_future=True)
                print(f"Cron: Imported {count} meetings from ICS.")
            except Exception as e:
                print(f"Cron ICS import failed: {e}")
        # Nightly sync from website at 03:10 (run after ICS or as alternative)
        if SOURCE_MEETINGS_WEB_URL and now.hour == 3 and now.minute == 10:
            try:
                count = import_meetings_from_webpage(SOURCE_MEETINGS_WEB_URL, weeks=12, replace_future=True)
                print(f"Cron: Imported {count} meetings from Website.")
            except Exception as e:
                print(f"Cron Website import failed: {e}")

if __name__ == "__main__":
    main()