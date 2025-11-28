from icalendar import Calendar, Event, Alarm
from datetime import datetime, timedelta
from django.utils import timezone
from typing import List
import pytz

def generate_ical_feed(user_holidays, calendar_name: str = "My Holidays", tz: str = "UTC") -> Calendar:
    """
    Generate a complete iCalendar feed from user's holidays
    
    Args:
        user_holidays: QuerySet of UserHoliday objects
        calendar_name: Name for the calendar
        tz: Timezone string
    
    Returns:
        Calendar object ready to export
    """
    cal = Calendar()
    
    # Required properties
    cal.add('prodid', '-//eld Holiday Calendar//EN')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('method', 'PUBLISH')
    
    # Calendar name and description
    cal.add('x-wr-calname', calendar_name)
    cal.add('x-wr-timezone', tz)
    cal.add('x-wr-caldesc', f'Personal holiday calendar from eld - {len(user_holidays)} celebrations')
    
    # Add each holiday as an event
    for user_holiday in user_holidays:
        holiday = user_holiday.holiday
        event = create_ical_event(holiday, user_holiday, tz)
        cal.add_component(event)
    
    return cal

def create_ical_event(holiday, user_holiday=None, tz: str = "UTC") -> Event:
    """
    Create an iCalendar event from a holiday
    
    Args:
        holiday: Holiday object
        user_holiday: UserHoliday object (optional, for reminders)
        tz: Timezone string
    
    Returns:
        Event object
    """
    event = Event()
    
    # Basic info
    event.add('summary', holiday.name)
    event.add('dtstart', holiday.date)
    event.add('dtend', holiday.date + timedelta(days=1))
    event.add('dtstamp', timezone.now())
    
    # Description
    description_parts = []
    
    if holiday.description:
        description_parts.append(holiday.description)
    
    # Add country flags
    flags = ' '.join([c.flag_emoji for c in holiday.countries.all()[:5]])
    if flags:
        description_parts.append(f"\n{flags}")
    
    # Add categories as text
    categories = ', '.join([cat.name for cat in holiday.categories.all()])
    if categories:
        description_parts.append(f"\nCategories: {categories}")
    
    # Add user notes if available
    if user_holiday and user_holiday.notes:
        description_parts.append(f"\n\nNotes: {user_holiday.notes}")
    
    # Add source attribution
    if holiday.sources:
        description_parts.append(f"\n\nData sources: {', '.join(holiday.sources[:3])}")
    
    description_parts.append("\n\n📅 From eld - Every Little Day")
    
    event.add('description', '\n'.join(description_parts))
    
    # Categories for filtering in calendar apps
    event_categories = [cat.name for cat in holiday.categories.all()]
    if event_categories:
        event.add('categories', event_categories)
    
    # Location (countries or Global)
    countries = [c.name for c in holiday.countries.all()[:3]]
    if countries:
        event.add('location', ', '.join(countries))
    elif holiday.is_global:
        event.add('location', 'Global')
    
    # Unique identifier
    event.add('uid', f'holiday-{holiday.id}-{holiday.date.year}@eld.app')
    
    # URL if available
    if holiday.wikipedia_url:
        event.add('url', holiday.wikipedia_url)
    
    # Status
    event.add('status', 'CONFIRMED')
    event.add('transp', 'TRANSPARENT')  # Doesn't block time
    
    # Add reminder/alarm if user has set one
    if user_holiday and user_holiday.reminder != 'none':
        alarm = Alarm()
        alarm.add('action', 'DISPLAY')
        alarm.add('description', f"Reminder: {holiday.name}")
        
        if user_holiday.reminder == '1day':
            alarm.add('trigger', timedelta(days=-1))
        elif user_holiday.reminder == 'morning':
            # 8 AM on the day
            alarm.add('trigger', timedelta(hours=-8))
        
        event.add_component(alarm)
    
    return event

def validate_ical_feed(cal: Calendar) -> bool:
    """Validate that the calendar is properly formed"""
    try:
        # Check required properties
        if not cal.get('version'):
            return False
        if not cal.get('prodid'):
            return False
        
        # Check we have at least one event
        events = [component for component in cal.walk() if component.name == "VEVENT"]
        if not events:
            return False
        
        return True
    except Exception:
        return False

def get_calendar_stats(user_holidays) -> dict:
    """Get statistics about a user's calendar"""
    from django.utils import timezone
    
    today = timezone.now().date()
    
    stats = {
        'total': user_holidays.count(),
        'upcoming': user_holidays.filter(holiday__date__gte=today).count(),
        'past': user_holidays.filter(holiday__date__lt=today).count(),
        'this_month': user_holidays.filter(
            holiday__date__year=today.year,
            holiday__date__month=today.month
        ).count(),
        'with_reminders': user_holidays.exclude(reminder='none').count(),
    }
    
    # Count by category
    stats['by_category'] = {}
    for uh in user_holidays:
        for cat in uh.holiday.categories.all():
            stats['by_category'][cat.name] = stats['by_category'].get(cat.name, 0) + 1
    
    # Next upcoming holiday
    next_holiday = user_holidays.filter(holiday__date__gte=today).order_by('holiday__date').first()
    if next_holiday:
        stats['next_holiday'] = {
            'name': next_holiday.holiday.name,
            'date': next_holiday.holiday.date,
            'days_until': (next_holiday.holiday.date - today).days
        }
    
    return stats