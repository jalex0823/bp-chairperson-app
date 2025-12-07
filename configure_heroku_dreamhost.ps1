# Heroku Configuration Script
# Run this to configure DreamHost MySQL database on Heroku

Write-Host "🔧 Setting Heroku environment variables for DreamHost MySQL..." -ForegroundColor Cyan

# Database Configuration
heroku config:set DB_HOST=mysql.therealbackporch.com --app backporch-chair-app
heroku config:set DB_PORT=3306 --app backporch-chair-app
heroku config:set DB_NAME=chairameeting --app backporch-chair-app
heroku config:set DB_USER=chairperson --app backporch-chair-app
heroku config:set "DB_PASSWORD=12!Gratitudeee" --app backporch-chair-app

# Email Configuration
heroku config:set MAIL_SERVER=smtp.dreamhost.com --app backporch-chair-app
heroku config:set MAIL_PORT=465 --app backporch-chair-app
heroku config:set MAIL_USE_SSL=True --app backporch-chair-app
heroku config:set MAIL_USE_TLS=False --app backporch-chair-app
heroku config:set MAIL_USERNAME=chair@therealbackporch.com --app backporch-chair-app
heroku config:set "MAIL_PASSWORD=therealbp2025!" --app backporch-chair-app
heroku config:set MAIL_DEFAULT_SENDER=chair@therealbackporch.com --app backporch-chair-app

# Remove DATABASE_URL so it uses the MySQL connection instead
heroku config:unset DATABASE_URL --app backporch-chair-app

Write-Host "✅ Heroku configuration complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Current Heroku config:" -ForegroundColor Yellow
heroku config --app backporch-chair-app
