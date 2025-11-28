import os
from celery import Celery
from celery.schedules import crontab
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eld.settings')

app = Celery('eld')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Periodic tasks with Beat
app.conf.beat_schedule = {
    # Refresh all holidays daily at 2 AM
    'refresh-holidays-daily': {
        'task': 'apps.holidays.tasks.refresh_all_holidays',
        'schedule': crontab(hour=2, minute=0),
    },
    
    # Send reminder emails daily at 9 AM
    'send-holiday-reminders': {
        'task': 'apps.calendars.tasks.send_daily_reminders',
        'schedule': crontab(hour=9, minute=0),
    },
    
    # Clean up old holiday data monthly
    'cleanup-old-holidays': {
        'task': 'apps.holidays.tasks.cleanup_old_data',
        'schedule': crontab(day_of_month=1, hour=3, minute=0),
    },
    
    # Generate weekly digest every Monday at 8 AM
    'weekly-digest': {
        'task': 'apps.calendars.tasks.send_weekly_digest',
        'schedule': crontab(day_of_week=1, hour=8, minute=0),
    },
    
    # Update holiday statistics every 6 hours
    'update-stats': {
        'task': 'apps.holidays.tasks.update_statistics',
        'schedule': timedelta(hours=6),
    },
}

# Celery configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')