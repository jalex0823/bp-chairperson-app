#!/usr/bin/env python3
"""
Heroku worker process for running the APScheduler background jobs.
This keeps the scheduler running separately from the web process.
"""

import os
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

# Load environment variables
load_dotenv()

# Import after loading env vars
from app import send_open_slot_reminder, send_day_of_chair_reminders

def run_scheduler():
    """Run the background scheduler for email reminders."""
    scheduler = BlockingScheduler()

    # Schedule weekly open slots reminder (every Sunday at 10 AM)
    scheduler.add_job(
        send_open_slot_reminder,
        CronTrigger(day_of_week='sun', hour=10),
        id='weekly-open-slots',
        replace_existing=True
    )

    # Schedule day-of chair reminders every morning at 6 AM (server local time)
    scheduler.add_job(
        send_day_of_chair_reminders,
        CronTrigger(hour=6),
        id='daily-day-of-reminders',
        replace_existing=True
    )

    print("🚀 Starting Back Porch Chair Portal scheduler...")
    print("📅 Weekly reminders scheduled for Sundays at 10 AM")
    print("📧 Day-of chair reminders scheduled daily at 6 AM")
    print("💡 Individual chair reminders scheduled dynamically when signups occur")

    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.shutdown()

if __name__ == '__main__':
    run_scheduler()