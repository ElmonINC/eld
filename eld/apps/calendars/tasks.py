from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
import logging

from apps.calendars.models import UserHoliday

logger = logging.getLogger(__name__)

@shared_task
def send_daily_reminders():
    """
    Send reminder emails for holidays coming up
    Runs daily at 9 AM
    """
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    
    sent_count = 0
    
    # 1 day before reminders
    one_day_reminders = UserHoliday.objects.filter(
        reminder='1day',
        reminder_sent=False,
        holiday__date=tomorrow
    ).select_related('user', 'holiday')
    
    for user_holiday in one_day_reminders:
        try:
            send_holiday_reminder_email(
                user_holiday.user,
                user_holiday.holiday,
                days_until=1
            )
            user_holiday.reminder_sent = True
            user_holiday.save()
            sent_count += 1
        except Exception as e:
            logger.error(f"Failed to send reminder for {user_holiday}: {e}")
    
    # Morning of reminders
    morning_reminders = UserHoliday.objects.filter(
        reminder='morning',
        reminder_sent=False,
        holiday__date=today
    ).select_related('user', 'holiday')
    
    for user_holiday in morning_reminders:
        try:
            send_holiday_reminder_email(
                user_holiday.user,
                user_holiday.holiday,
                days_until=0
            )
            user_holiday.reminder_sent = True
            user_holiday.save()
            sent_count += 1
        except Exception as e:
            logger.error(f"Failed to send reminder for {user_holiday}: {e}")
    
    logger.info(f"Sent {sent_count} holiday reminders")
    return {'sent': sent_count}

@shared_task
def send_weekly_digest():
    """
    Send weekly digest of upcoming holidays
    Runs every Monday at 8 AM
    """
    from apps.calendars.models import UserCalendar
    from apps.accounts.models import UserProfile
    
    today = timezone.now().date()
    week_end = today + timedelta(days=7)
    
    sent_count = 0
    
    # Get users who want weekly digest
    profiles = UserProfile.objects.filter(
        weekly_digest=True
    ).select_related('user')
    
    for profile in profiles:
        try:
            # Get user's upcoming holidays
            upcoming = UserHoliday.objects.filter(
                user=profile.user,
                holiday__date__gte=today,
                holiday__date__lte=week_end
            ).select_related('holiday').order_by('holiday__date')
            
            if upcoming.exists():
                send_weekly_digest_email(profile.user, upcoming)
                sent_count += 1
        except Exception as e:
            logger.error(f"Failed to send digest to {profile.user}: {e}")
    
    logger.info(f"Sent {sent_count} weekly digests")
    return {'sent': sent_count}

def send_holiday_reminder_email(user, holiday, days_until):
    """Send reminder email for a specific holiday"""
    
    if days_until == 0:
        subject = f"🎉 Today is {holiday.name}!"
        message = f"Don't forget to celebrate {holiday.name} today!"
    else:
        subject = f"⏰ {holiday.name} is tomorrow!"
        message = f"{holiday.name} is coming up tomorrow ({holiday.date.strftime('%B %d, %Y')})"
    
    if holiday.description:
        message += f"\n\n{holiday.description}"
    
    message += f"\n\nView in your calendar: {settings.SITE_URL}/my-calendar/"
    message += f"\n\n🎊 From eld - Every Little Day"
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

def send_weekly_digest_email(user, upcoming_holidays):
    """Send weekly digest of upcoming holidays"""
    
    subject = f"📅 Your holidays this week ({len(upcoming_holidays)} celebrations)"
    
    message = f"Hello!\n\nHere are your upcoming celebrations this week:\n\n"
    
    for user_holiday in upcoming_holidays:
        holiday = user_holiday.holiday
        days = (holiday.date - timezone.now().date()).days
        
        day_text = "Today!" if days == 0 else f"In {days} day{'s' if days != 1 else ''}"
        message += f"• {holiday.name} - {holiday.date.strftime('%A, %B %d')} ({day_text})\n"
        
        if holiday.description:
            message += f"  {holiday.description[:100]}...\n"
        message += "\n"
    
    message += f"\nView your full calendar: {settings.SITE_URL}/my-calendar/"
    message += f"\n\n🎉 Happy celebrating!"
    message += f"\n\n---\nFrom eld - Every Little Day"
    message += f"\n\nUnsubscribe from weekly digests in your account settings."
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

@shared_task
def reset_reminder_flags():
    """
    Reset reminder_sent flags for past holidays
    Runs daily
    """
    today = timezone.now().date()
    
    updated = UserHoliday.objects.filter(
        reminder_sent=True,
        holiday__date__lt=today
    ).update(reminder_sent=False)
    
    logger.info(f"Reset {updated} reminder flags")
    return {'reset': updated}