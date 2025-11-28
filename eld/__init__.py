"""
Create these empty __init__.py files in these directories:

eld/__init__.py - Main project package
apps/__init__.py - Apps package
apps/holidays/__init__.py - Holidays app
apps/holidays/services/__init__.py - Services package
apps/holidays/management/__init__.py - Management package
apps/holidays/management/commands/__init__.py - Commands package
apps/calendars/__init__.py - Calendars app
apps/accounts/__init__.py - Accounts app
"""

# For eld/__init__.py, add Celery configuration:
# This ensures that the Celery app is loaded when Django starts

from __future__ import absolute_import, unicode_literals

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

__all__ = ('celery_app',)