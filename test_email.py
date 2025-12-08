#!/usr/bin/env python
"""
Quick email test script for eld
Run this to test your SMTP configuration before using it in the app.

Usage:
    python test_email.py your-email@example.com
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eld.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email(to_email):
    """Send a test email"""
    print(f"📧 Testing email configuration...")
    print(f"   Backend: {settings.EMAIL_BACKEND}")
    print(f"   Host: {settings.EMAIL_HOST}")
    print(f"   Port: {settings.EMAIL_PORT}")
    print(f"   From: {settings.DEFAULT_FROM_EMAIL}")
    print(f"   To: {to_email}")
    print()
    
    try:
        send_mail(
            subject='🎉 Test Email from eld',
            message='Congratulations! Your email configuration is working correctly. You should now receive verification emails when users sign up.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            fail_silently=False,
        )
        print("✅ Email sent successfully!")
        print(f"   Check your inbox at {to_email} (and spam folder)")
        return True
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        print()
        print("Common issues:")
        print("  - Check your .env file has correct EMAIL_* settings")
        print("  - For Gmail: Make sure you're using an App Password")
        print("  - For SendGrid: Make sure EMAIL_HOST_USER='apikey'")
        print("  - Check firewall isn't blocking port 587")
        print()
        print("See EMAIL_SETUP.md for detailed configuration guide.")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python test_email.py your-email@example.com")
        sys.exit(1)
    
    to_email = sys.argv[1]
    success = test_email(to_email)
    sys.exit(0 if success else 1)

