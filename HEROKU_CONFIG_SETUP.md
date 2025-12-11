# Heroku Configuration Setup

## Problem
Getting 500 Internal Server Error because Heroku doesn't have the DreamHost database credentials.

## Solution: Set Environment Variables on Heroku

### Option 1: Using Heroku Dashboard (Easiest)
1. Go to: https://dashboard.heroku.com/apps/backporch-chair-app/settings
2. Click **"Reveal Config Vars"**
3. Add the following variables:

```
DB_HOST = mysql.therealbackporch.com
DB_PORT = 3306
DB_NAME = chairameeting
DB_USER = chairperson
DB_PASSWORD = [your actual database password]
SECRET_KEY = [generate a secure random key]
MAIL_USERNAME = [your email username]
MAIL_PASSWORD = [your email password]
MAIL_DEFAULT_SENDER = noreply@backporchmeetings.org
```

### Option 2: Using Heroku CLI
```bash
heroku config:set DB_HOST=mysql.therealbackporch.com --app backporch-chair-app
heroku config:set DB_PORT=3306 --app backporch-chair-app
heroku config:set DB_NAME=chairameeting --app backporch-chair-app
heroku config:set DB_USER=chairperson --app backporch-chair-app
heroku config:set DB_PASSWORD=your_actual_password --app backporch-chair-app
heroku config:set SECRET_KEY=your_secret_key --app backporch-chair-app
heroku config:set MAIL_USERNAME=your_email --app backporch-chair-app
heroku config:set MAIL_PASSWORD=your_email_password --app backporch-chair-app
heroku config:set MAIL_DEFAULT_SENDER=noreply@backporchmeetings.org --app backporch-chair-app
```

### Required Variables
- **DB_HOST**: Your DreamHost MySQL server hostname
- **DB_PORT**: MySQL port (usually 3306)
- **DB_NAME**: Your database name
- **DB_USER**: Your database username
- **DB_PASSWORD**: Your database password (check your .env file)
- **SECRET_KEY**: Flask secret key for sessions (generate a random string)
- **MAIL_USERNAME**: SMTP username for sending emails
- **MAIL_PASSWORD**: SMTP password
- **MAIL_DEFAULT_SENDER**: Default sender email address

### Optional Variables
- **MAIL_SERVER**: smtp.dreamhost.com (has default)
- **MAIL_PORT**: 465 (has default)
- **MAIL_USE_SSL**: True (has default)

### After Setting Config Vars
Heroku will automatically restart your app. Wait 30-60 seconds, then visit:
https://backporch-chair-app-35851db28c9c.herokuapp.com/

### Get Values from Your .env File
Your local .env file has these values. You can copy them to Heroku config vars.

**DO NOT** commit your .env file to Git - it contains sensitive passwords!
