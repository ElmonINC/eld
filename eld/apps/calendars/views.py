from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from icalendar import Calendar, Event
from datetime import datetime, timedelta

from apps.calendars.models import UserCalendar, UserHoliday

@login_required
def my_calendar(request):
    """User's personal calendar dashboard"""
    calendar, created = UserCalendar.objects.get_or_create(user=request.user)
    
    # Get user's holidays
    user_holidays = UserHoliday.objects.filter(
        user=request.user
    ).select_related('holiday').prefetch_related(
        'holiday__countries',
        'holiday__categories'
    ).order_by('holiday__date')
    
    # Upcoming holidays (next 30 days)
    today = timezone.now().date()
    upcoming = user_holidays.filter(
        holiday__date__gte=today,
        holiday__date__lte=today + timedelta(days=30)
    )
    
    # Past holidays this year
    year_start = today.replace(month=1, day=1)
    past = user_holidays.filter(
        holiday__date__gte=year_start,
        holiday__date__lt=today
    )
    
    # Future holidays
    future = user_holidays.filter(
        holiday__date__gt=today + timedelta(days=30)
    )
    
    context = {
        'calendar': calendar,
        'upcoming': upcoming,
        'past': past,
        'future': future,
        'total_count': user_holidays.count(),
    }
    
    return render(request, 'calendars/my_calendar.html', context)

def calendar_feed(request, feed_token):
    """
    Generate iCal feed for user's calendar
    Compatible with Google Calendar, Apple Calendar, Outlook
    """
    calendar_obj = get_object_or_404(UserCalendar, feed_token=feed_token)
    
    # Create iCalendar
    cal = Calendar()
    cal.add('prodid', '-//eld - Holiday Calendar//EN')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('method', 'PUBLISH')
    cal.add('x-wr-calname', f"{calendar_obj.user.get_full_name() or calendar_obj.user.email}'s Holidays")
    cal.add('x-wr-timezone', calendar_obj.timezone)
    cal.add('x-wr-caldesc', 'Personal holiday calendar from eld')
    
    # Add each holiday as an event
    user_holidays = UserHoliday.objects.filter(
        user=calendar_obj.user
    ).select_related('holiday')
    
    for user_holiday in user_holidays:
        holiday = user_holiday.holiday
        
        event = Event()
        event.add('summary', holiday.name)
        event.add('dtstart', holiday.date)
        event.add('dtend', holiday.date + timedelta(days=1))
        event.add('dtstamp', timezone.now())
        
        # Description
        description_parts = []
        if holiday.description:
            description_parts.append(holiday.description)
        
        if holiday.country_flags:
            description_parts.append(f"\n{holiday.country_flags}")
        
        if user_holiday.notes:
            description_parts.append(f"\n\nNotes: {user_holiday.notes}")
        
        event.add('description', '\n'.join(description_parts))
        
        # Categories
        categories = [cat.name for cat in holiday.categories.all()]
        if categories:
            event.add('categories', categories)
        
        # Location (countries)
        countries = [c.name for c in holiday.countries.all()[:3]]
        if countries:
            event.add('location', ', '.join(countries))
        elif holiday.is_global:
            event.add('location', 'Global')
        
        # UID
        event.add('uid', f'holiday-{holiday.id}@eld.app')
        
        # Add reminder if set
        if user_holiday.reminder != 'none':
            from icalendar import Alarm
            alarm = Alarm()
            alarm.add('action', 'DISPLAY')
            alarm.add('description', f"Reminder: {holiday.name}")
            
            if user_holiday.reminder == '1day':
                alarm.add('trigger', timedelta(days=-1))
            elif user_holiday.reminder == 'morning':
                alarm.add('trigger', timedelta(hours=-8))
            
            event.add_component(alarm)
        
        cal.add_component(event)
    
    # Return as .ics file
    response = HttpResponse(cal.to_ical(), content_type='text/calendar; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="eld-calendar.ics"'
    return response

@login_required
def download_ics(request):
    """Download .ics file directly"""
    calendar, _ = UserCalendar.objects.get_or_create(user=request.user)
    return calendar_feed(request, calendar.feed_token)

@login_required
def bulk_add(request):
    """Bulk add holidays (for special occasions)"""
    if request.method == 'POST':
        holiday_ids = request.POST.getlist('holiday_ids[]')
        
        calendar, _ = UserCalendar.objects.get_or_create(user=request.user)
        
        added = 0
        for holiday_id in holiday_ids:
            _, created = UserHoliday.objects.get_or_create(
                user=request.user,
                holiday_id=holiday_id
            )
            if created:
                added += 1
        
        return JsonResponse({
            'success': True,
            'added': added,
            'message': f'Added {added} holidays to your calendar!'
        })
    
    return JsonResponse({'success': False}, status=400)