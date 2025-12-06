#!/usr/bin/env python3
"""
Test script for Back Porch Chair App email configuration.
Run this to verify email sending works before deploying.
"""

import os
from dotenv import load_dotenv
from flask import Flask
from flask_mail import Mail, Message

# Load environment variables
load_dotenv()

# Create minimal Flask app for testing
app = Flask(__name__)
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 465))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'False').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)

def test_email():
    """Send a test email to verify configuration."""
    with app.app_context():
        try:
            # Test email to yourself
            recipient = os.getenv('MAIL_USERNAME')  # Send to yourself for testing

            msg = Message(
                subject='Back Porch Chair App - Email Test',
                recipients=[recipient],
                body="""Hello!

This is a test email from your Back Porch Chair Portal.

If you received this, your email configuration is working correctly!

Features enabled:
- 24-hour chair reminders
- Weekly open slots notifications
- Calendar subscriptions (.ics export)

Best regards,
Back Porch Chair Portal
"""
            )

            mail.send(msg)
            print("✅ Test email sent successfully!")
            print(f"📧 Sent to: {recipient}")
            print("📬 Check your inbox (and spam folder) for the test email.")

        except Exception as e:
            print(f"❌ Email test failed: {e}")
            print("\nTroubleshooting tips:")
            print("1. Verify your email credentials are correct")
            print("2. Check if DreamHost email account is properly set up")
            print("3. Ensure you're not blocked by firewall/antivirus")
            print("4. Try sending from DreamHost webmail first")

if __name__ == '__main__':
    print("🧪 Testing Back Porch Chair App Email Configuration")
    print("=" * 50)
    test_email()