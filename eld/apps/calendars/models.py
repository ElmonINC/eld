from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from eld.apps.holidays.models import Holiday

class UserCalendar(models.Model):
    """User's personal calendar with unique feed URL"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='calendar')
    name = models.CharField(max_length=100, default="My Holiday Calendar")
    
    # Unique iCal feed URL token
    feed_token = models.CharField(max_length=64, unique=True, db_index=True)
    
    # Settings
    timezone = models.CharField(max_length=50, default='UTC')
    is_public = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.feed_token:
            self.feed_token = get_random_string(64)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.email}'s Calendar"
    
    @property
    def feed_url(self):
        """Generate the webcal:// URL for this calendar"""
        from django.conf import settings
        base_url = settings.SITE_URL.replace('http://', '').replace('https://', '')
        return f"webcal://{base_url}/calendar/feed/{self.feed_token}/"
    
    @property
    def ics_url(self):
        """Generate the https:// .ics URL for download"""
        from django.conf import settings
        return f"{settings.SITE_URL}/calendar/feed/{self.feed_token}/"

class UserHoliday(models.Model):
    """User's saved holidays with reminders"""
    REMINDER_CHOICES = [
        ('none', 'No Reminder'),
        ('1day', '1 Day Before'),
        ('morning', 'Morning Of'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_holidays')
    holiday = models.ForeignKey(Holiday, on_delete=models.CASCADE, related_name='saved_by')
    
    # Reminder settings
    reminder = models.CharField(max_length=10, choices=REMINDER_CHOICES, default='none')
    reminder_sent = models.BooleanField(default=False)
    
    # Custom notes
    notes = models.TextField(blank=True)
    
    # Timestamps
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['holiday__date']
        unique_together = [['user', 'holiday']]
    
    def __str__(self):
        return f"{self.user.email} - {self.holiday.name}"