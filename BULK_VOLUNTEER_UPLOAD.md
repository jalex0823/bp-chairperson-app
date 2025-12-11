# Bulk Volunteer Date Upload Feature

## Overview

The bulk volunteer date upload feature allows chairpersons to register for multiple hosting dates at once using a CSV file instead of manually selecting each date on the calendar. This is particularly useful for users who want to volunteer for multiple dates at the beginning of a month or for advance planning.

## How It Works

### For Users

1. **Download Template**
   - Navigate to your Dashboard or Profile page
   - Click "Bulk Volunteer Upload" button
   - Click "Download CSV Template" to get the properly formatted CSV file
   - Template includes 7 example dates (next 7 days) that you can replace

2. **Fill Out CSV**
   - Open the CSV in Excel, Google Sheets, or any spreadsheet application
   - Enter dates in YYYY-MM-DD format (e.g., 2025-12-25)
   - Choose time preference for each date:
     - `any` - Available any time
     - `morning` - Before 12 PM
     - `afternoon` - 12 PM to 6 PM
     - `evening` - After 6 PM
   - Optionally add notes for each date (max 500 characters)

3. **Upload CSV**
   - Save your file as CSV format
   - Return to the Bulk Volunteer Upload page
   - Select your CSV file
   - Click "Upload CSV"

4. **Review Results**
   - System processes each row and reports:
     - ✅ Success: Number of dates successfully registered
     - ⚠️ Warnings: Duplicate dates or dates you've already volunteered for
     - ❌ Errors: Invalid dates, past dates, or formatting issues
   - Email confirmations sent for each successfully registered date

### CSV Format

```csv
Date (YYYY-MM-DD),Time Preference,Notes (Optional)
2025-12-15,morning,Available before noon
2025-12-22,evening,Prefer after 6 PM
2026-01-05,any,Flexible schedule
2026-01-12,afternoon,
```

**Important:**
- Header row (first line) must not be modified
- Date format must be YYYY-MM-DD exactly
- Time preference must be lowercase: `any`, `morning`, `afternoon`, or `evening`
- Notes are optional (can be left blank)
- Empty rows are automatically skipped

## Features

### Validation
- ✅ Date format validation (must be YYYY-MM-DD)
- ✅ Future date enforcement (no past dates)
- ✅ Time preference validation (must be valid option)
- ✅ Duplicate detection (won't re-register existing dates)
- ✅ Character limits (notes max 500 characters)
- ✅ CSV header validation (ensures correct template format)

### Error Handling
- Individual row errors don't stop processing
- Detailed error messages with row numbers
- Successful rows are committed even if some rows fail
- Maximum 10 errors displayed (with count of remaining errors)

### Email Notifications
- Automatic confirmation email for each successfully registered date
- Same format as single-date volunteer confirmations
- Includes date, time preference, and next steps

## Access Points

Users can access the bulk upload feature from:
1. **Dashboard** - "Bulk Volunteer Upload" button in Quick Actions
2. **Profile Page** - "Bulk Volunteer Upload" button in Chairperson Resources
3. **Direct URL** - `/volunteer/bulk-upload`

## Routes

### `/volunteer/bulk-template` (GET)
- Generates and downloads CSV template
- Includes header row and 7 example dates
- Pre-filled with next 7 days as examples
- Content-Type: `text/csv`
- Filename: `volunteer_dates_template.csv`

### `/volunteer/bulk-upload` (GET, POST)
- GET: Shows upload form with instructions
- POST: Processes uploaded CSV file
- Requires authentication (`@login_required`)
- Validates CSV format and content
- Creates ChairpersonAvailability records
- Sends confirmation emails
- Redirects to profile with success/error messages

## Technical Details

### Database
- Uses existing `ChairpersonAvailability` model
- No schema changes required
- Maintains data integrity with existing single-date system

### Dependencies
- Python `csv` module (standard library)
- `io.StringIO` for in-memory CSV processing
- `io.TextIOWrapper` for file stream handling
- Existing email system for confirmations

### Limits
- No hard limit on number of dates per upload
- Practical limit suggested: ~100 dates per file
- Rate limiting may apply via existing Flask rate limiting
- File size limited by Flask's MAX_CONTENT_LENGTH setting

## User Experience

### Benefits
1. **Time Saving** - Register for multiple dates in one action
2. **Planning** - Can plan ahead for entire month/quarter
3. **Flexibility** - Different time preferences per date
4. **Efficiency** - No need to click through calendar multiple times
5. **Offline Preparation** - Can prepare CSV offline, upload when ready

### Workflow Comparison

**Before (Single Date):**
1. Click on calendar date
2. Fill form for one date
3. Submit
4. Repeat for each date (5-10 clicks per date)

**After (Bulk Upload):**
1. Download template once
2. Fill all dates in spreadsheet
3. Upload CSV once
4. All dates registered at once

## Future Enhancements

Potential improvements:
- Excel (.xlsx) file support
- Bulk edit existing volunteer dates
- Bulk delete volunteer dates
- Download current volunteer dates as CSV
- Import from Google Calendar
- Recurring date patterns (e.g., "every Monday")

## Testing

Test scenarios:
- ✅ Valid CSV with multiple dates
- ✅ CSV with past dates (should error)
- ✅ CSV with duplicate dates
- ✅ CSV with invalid time preferences
- ✅ CSV with malformed dates
- ✅ Empty CSV file
- ✅ CSV with mixed valid/invalid rows
- ✅ Non-CSV file upload
- ✅ CSV with missing headers

## Support

For issues or questions:
- Contact admin team at backporchmeetings@outlook.com
- Include error messages if upload fails
- Attach CSV file (remove any private notes first)
