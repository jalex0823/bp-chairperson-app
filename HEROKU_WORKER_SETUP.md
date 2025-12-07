# Heroku Worker Setup for Email Reminders

## What Was Fixed

### 1. iCal Attachments Added ✅
All confirmation and reminder emails now include `.ics` calendar attachments that users can add to their calendar apps (Outlook, Google Calendar, Apple Calendar, etc.).

**Files Modified:**
- `app.py`:
  - Added `generate_meeting_ical()` function to create iCal events
  - Updated `send_email()` to support attachments
  - Updated `send_chair_confirmation()` to include iCal attachment
  - Updated `send_chair_reminder()` to include iCal attachment
  - Added `from sqlalchemy import func` import

**Features in iCal Attachment:**
- Meeting title (prefixed with "CHAIR:" so you know you're chairing)
- Date and time
- Duration
- Location (Zoom link)
- Description with meeting details
- **Built-in reminders:**
  - 24 hours before meeting
  - 1 hour before meeting

### 2. Worker Process Updated ✅
The background worker now checks **every hour** for meetings that need reminder emails.

**Files Modified:**
- `worker.py`:
  - Added `check_and_send_reminders` to imports
  - Added hourly job to check for 24-hour and 1-hour reminders
  - Runs at the top of every hour (XX:00)

**Current Worker Schedule:**
- **Hourly (new!):** Check for meetings needing 24h or 1h reminders
- **Daily at 6 AM:** Send day-of reminders to chairs
- **Weekly (Sundays at 10 AM):** Send open slots reminder

## Required: Enable Worker Dyno on Heroku

⚠️ **CRITICAL:** The worker dyno must be running for reminder emails to be sent!

### Check Worker Status

1. Go to: https://dashboard.heroku.com/apps/backporch-chair-app/resources
2. Look for the **worker** dyno
3. Check if it shows "ON" or "OFF"

### If Worker is OFF:

1. Click the edit icon (pencil) next to "worker python worker.py"
2. Toggle the switch to **ON**
3. Click **Confirm**

**Note:** The worker dyno may incur additional Heroku costs depending on your plan.

### Alternative: Use Heroku Scheduler (Free Tier)

If you want to avoid worker dyno costs, you can use Heroku Scheduler (free add-on):

1. Add Heroku Scheduler:
   ```bash
   heroku addons:create scheduler:standard --app backporch-chair-app
   ```

2. Configure hourly job:
   ```bash
   heroku addons:open scheduler --app backporch-chair-app
   ```

3. Add a new job:
   - **Command:** `python reminder_worker.py`
   - **Frequency:** Every hour
   - **Save**

## How Reminders Work

### When You Sign Up for a Meeting:
1. **Immediate:** Confirmation email sent with iCal attachment
2. **24 hours before:** Reminder email with iCal attachment
3. **1 hour before:** Final reminder email with iCal attachment

### Email Timeline Example:
If you sign up to chair on **December 10, 2025 at 3:30 PM**:

- **Now:** "Confirmed: You're chairing..." email (with .ics attachment)
- **December 9 at 3:00 PM:** "Reminder: You're chairing tomorrow" email
- **December 10 at 2:30 PM:** "Starting soon: in 1 hour" email

## Testing the Worker

### Check Worker Logs:
```bash
heroku logs --tail --ps worker --app backporch-chair-app
```

Look for:
```
🚀 Starting Back Porch Chair Portal scheduler...
📅 Weekly reminders scheduled for Sundays at 10 AM
📧 Day-of chair reminders scheduled daily at 6 AM
⏰ Meeting reminders scheduled hourly (24h and 1h before)
```

### Test Email Sending:
The worker runs every hour at XX:00. If you have a meeting:
- **24-25 hours from now** → You'll get a 24h reminder at the next hour
- **55-65 minutes from now** → You'll get a 1h reminder at the next hour

## Troubleshooting

### Not Receiving Reminder Emails?

1. **Check worker is running:**
   ```bash
   heroku ps --app backporch-chair-app
   ```
   Should show: `worker.1: up YYYY/MM/DD HH:MM:SS`

2. **Check worker logs:**
   ```bash
   heroku logs --tail --ps worker --app backporch-chair-app
   ```

3. **Check email configuration:**
   Make sure `MAIL_SERVER`, `MAIL_USERNAME`, `MAIL_PASSWORD` are set in Heroku config vars

4. **Check spam folder:**
   Reminder emails might be filtered

### iCal Attachment Not Working?

- The `.ics` file should appear as an attachment in the email
- You can click to add it to your calendar
- If it doesn't work, check your email client settings for calendar invites
- Gmail/Outlook should show an "Add to Calendar" button

## Dashboard Stats

The dashboard stats show:
- **Upcoming Meetings:** Meetings you're scheduled to chair in the future
- **Total Meetings Chaired:** Past meetings you've chaired
- **Volunteer Signups:** Days you've volunteered to be available
- **Recent Service:** Meetings you've chaired in the last 30 days

If stats show zero, it means:
- You're looking at local database (SQLite) but signed up on production (MySQL)
- Or you haven't actually signed up for any meetings yet

Production data is on Heroku's MySQL database, local testing uses SQLite.

## Next Steps

1. ✅ Enable the worker dyno on Heroku (see instructions above)
2. ✅ Sign up for a test meeting on production
3. ✅ Check your email for confirmation with iCal attachment
4. ✅ Wait for reminder emails (24h and 1h before)
5. ✅ Verify dashboard stats update correctly

## Support

If you continue to have issues:
- Check Heroku logs: `heroku logs --tail --app backporch-chair-app`
- Check worker logs: `heroku logs --tail --ps worker --app backporch-chair-app`
- Verify email config: `heroku config --app backporch-chair-app | grep MAIL`
