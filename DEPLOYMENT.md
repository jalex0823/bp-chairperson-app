# Back Porch Chair Portal - Deployment Guide

## 🚀 Heroku Deployment (Recommended)

### Prerequisites
1. Create a [Heroku account](https://heroku.com)
2. Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

### Step-by-Step Deployment

1. **Login to Heroku**:
   ```bash
   heroku login
   ```

2. **Create Heroku App**:
   ```bash
   heroku create your-back-porch-app-name
   ```

3. **Set environment variables**:
   ```bash
   heroku config:set SECRET_KEY=your-generated-secret-key
   heroku config:set DATABASE_URL=postgresql://chairperson:12!Gratitudeee@your-db-host:5432/your-db-name
   heroku config:set MAIL_SERVER=smtp.dreamhost.com
   heroku config:set MAIL_PORT=465
   heroku config:set MAIL_USE_SSL=True
   heroku config:set MAIL_USERNAME=chair@therealbackporch.com
   heroku config:set MAIL_PASSWORD=therealbp2025!
   heroku config:set MAIL_DEFAULT_SENDER=chair@therealbackporch.com
   heroku config:set FLASK_ENV=production
   ```

4. **Deploy to Heroku**:
   ```bash
   git init
   git add .
   git commit -m "Initial deployment"
   git push heroku main
   ```

5. **Initialize Database**:
   ```bash
   heroku run flask --app app.py init-db
   ```

6. **Scale the Worker Process**:
   ```bash
   heroku ps:scale worker=1
   ```

7. **Open Your App**:
   ```bash
   heroku open
   ```

## 🔧 Alternative: Railway

1. Go to [Railway.app](https://railway.app)
2. Connect your GitHub repository
3. Set environment variables in Railway dashboard
4. Deploy automatically

## 📧 Email Testing

After deployment, test email:
```bash
heroku run python test_email.py
```

## 🌐 Domain Setup (Optional)

To use a custom domain:
```bash
heroku domains:add chair.backporchmeetings.org
```
Then update your DNS settings.

## 💡 Production Notes

- SQLite works for small apps, but consider PostgreSQL for larger scale
- Monitor your Heroku logs: `heroku logs --tail`
- Backups: Use `heroku pg:backups` if you switch to PostgreSQL
- SSL is included with Heroku custom domains

## 🆘 Troubleshooting

**App won't start**: Check logs with `heroku logs --tail`

**Email not working**: Verify SMTP credentials and check spam folder

**Scheduler not running**: Ensure worker process is scaled with `heroku ps:scale worker=1`