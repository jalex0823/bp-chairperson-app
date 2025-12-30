# Safari Login Fix - Deployment Instructions

## Problem
Safari on Mac was showing the public landing page instead of the logged-in dashboard after successful login. This was caused by Safari's strict cookie handling policies.

## Changes Made

### 1. Session Cookie Configuration (`config.py`)
Added Safari-compatible session cookie settings:

```python
# Session Cookie Configuration (Safari Compatibility)
SESSION_COOKIE_SECURE = True  # Auto-detected for production
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access
SESSION_COOKIE_SAMESITE = 'Lax'  # Safari-compatible
PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
SESSION_COOKIE_NAME = 'bp_session'  # Custom name
```

Key points:
- **SameSite=Lax**: Allows cookies to be sent with top-level navigations (compatible with Safari)
- **HttpOnly**: Prevents JavaScript access (security)
- **Secure**: Only sent over HTTPS in production (auto-detected)
- **Permanent lifetime**: Session persists for 24 hours

### 2. Login Route Updates (`app.py`)
Enhanced login to explicitly set session as permanent:

```python
session.permanent = True  # Use PERMANENT_SESSION_LIFETIME
session["user_id"] = user.id
session.modified = True  # Force session save
```

### 3. Response Headers (`app.py`)
Added Safari-specific cache control headers:

```python
if 'Set-Cookie' in response.headers:
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
```

## Deployment to Heroku

### Option 1: Using Heroku CLI (if logged in)
```bash
cd /Users/jalex0823/Documents/GitHub/bp-chairperson-app
git push heroku main
```

### Option 2: Using Heroku Dashboard (Recommended)
1. Go to https://dashboard.heroku.com/apps/backporch-chair-app
2. Navigate to the **Deploy** tab
3. Under "Deployment method", ensure **GitHub** is connected
4. Scroll to "Manual deploy" section
5. Select branch: **main**
6. Click **Deploy Branch**
7. Wait for deployment to complete

### Option 3: Auto-deploy from GitHub
1. Go to https://dashboard.heroku.com/apps/backporch-chair-app
2. Navigate to the **Deploy** tab
3. Under "Automatic deploys", click **Enable Automatic Deploys** for the main branch
4. Future commits to main will auto-deploy

## Testing After Deployment

### 1. Test in Safari on Mac
1. Open Safari
2. Go to https://backporch-chair-app-35851db28c9c.herokuapp.com
3. Clear cookies: Safari > Settings > Privacy > Manage Website Data > Remove All
4. Try logging in with your credentials
5. Verify you see the logged-in dashboard (with navigation showing Calendar, Today, Admin, etc.)
6. Refresh the page - you should stay logged in

### 2. Check Safari Console (if still having issues)
1. Safari > Settings > Advanced > Show features for web developers
2. Develop menu > Show Web Inspector
3. Go to Storage tab > Cookies
4. Look for `bp_session` cookie
5. Verify attributes:
   - Secure: Yes
   - HttpOnly: Yes
   - SameSite: Lax

### 3. Verify Session Persistence
1. Log in successfully
2. Open a new tab to the same site
3. You should already be logged in
4. Close and reopen Safari
5. Return to site - should still be logged in (within 24 hours)

## Common Safari Issues and Solutions

### Issue: "Logged in successfully" but still see landing page
**Solution**: Check that the Heroku app is accessed via HTTPS (not HTTP)

### Issue: Cookies not being saved
**Solution**: 
1. Safari > Settings > Privacy
2. Uncheck "Prevent cross-site tracking" for testing
3. Ensure "Block all cookies" is NOT checked

### Issue: "Invalid email or password" on correct credentials
**Solution**: Check the mobile password trim feature is working (already enabled)

## Configuration Variables on Heroku

You can verify/set these via Heroku dashboard under Settings > Config Vars:

```
SESSION_COOKIE_SECURE = true  # (optional - auto-detected)
PERMANENT_SESSION_LIFETIME = 86400  # (optional - default 24h)
```

## Rollback Instructions

If you need to rollback:

```bash
heroku releases --app backporch-chair-app
heroku rollback v[VERSION_NUMBER] --app backporch-chair-app
```

Or via dashboard:
1. More > Rollback to this version (on previous release)

## Git Commit Reference

The Safari fixes are in commit: `410b4df`
- Message: "Fix Safari session cookie handling - add SameSite=Lax, HttpOnly, and proper Secure flag configuration"
- Files changed: `config.py`, `app.py`

## Status

- ✅ Changes committed to local repository
- ✅ Changes pushed to GitHub (main branch)
- ⏳ Awaiting deployment to Heroku production

## Next Steps

1. Deploy to Heroku (use Option 2 above - Heroku Dashboard)
2. Test login in Safari on Mac
3. Verify session persistence across page refreshes
4. Test on other browsers to ensure no regression
5. Monitor audit logs for any login issues
