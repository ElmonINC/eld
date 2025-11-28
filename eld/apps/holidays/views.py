from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.cache import cache_page
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.cache import cache
from django.db.models import Q
import hashlib

from eld.apps.holidays.models import Holiday, Country, HolidayCategory
from eld.apps.calendars.models import UserHoliday, UserCalendar
from eld.apps.holidays.decorators import cache_queryset

def discovery_view(request):
    """Main holiday discovery page"""
    view_type = request.GET.get('view', 'week')
    
    context = {
        'view_type': view_type,
        'countries': Country.objects.all().order_by('name'),
        'categories': HolidayCategory.objects.all(),
    }
    
    return render(request, 'holidays/discovery.html', context)

@cache_queryset(timeout=3600, key_prefix='holidays_filtered')
def get_cached_holidays(start_date, end_date, filters):
    """Get holidays with caching"""
    holidays = Holiday.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    ).prefetch_related('countries', 'categories').order_by('date')
    
    # Apply filters from dict
    if filters.get('search'):
        holidays = holidays.filter(
            Q(name__icontains=filters['search']) | 
            Q(description__icontains=filters['search'])
        )
    
    if filters.get('country'):
        holidays = holidays.filter(
            Q(countries__code=filters['country']) | Q(is_global=True)
        )
    
    if filters.get('category'):
        holidays = holidays.filter(categories__slug=filters['category'])
    
    return holidays.distinct()

def week_view(request):
    """Next 7 days view with countdowns"""
    today = timezone.now().date()
    week_end = today + timedelta(days=7)
    
    # Build filters dict
    filters = {
        'search': request.GET.get('search', '').strip(),
        'country': request.GET.get('country', ''),
        'category': request.GET.get('category', ''),
    }
    
    # Use cached query
    holidays = get_cached_holidays(today, week_end, filters)
    
    # Check if user has saved each holiday
    saved_holiday_ids = []
    if request.user.is_authenticated:
        saved_holiday_ids = list(
            UserHoliday.objects.filter(
                user=request.user
            ).values_list('holiday_id', flat=True)
        )
    
    context = {
        'holidays': holidays,
        'saved_holiday_ids': saved_holiday_ids,
    }
    
    if request.htmx:
        return render(request, 'holidays/partials/holiday_list.html', context)
    
    return render(request, 'holidays/week_view.html', context)

def month_view(request):
    """This month and next month view"""
    today = timezone.now().date()
    current_month_start = today.replace(day=1)
    
    # Get next 2 months
    if today.month == 12:
        next_month = today.replace(year=today.year + 1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month + 1, day=1)
    
    if next_month.month == 12:
        month_after = next_month.replace(year=next_month.year + 1, month=1, day=1)
    else:
        month_after = next_month.replace(month=next_month.month + 1, day=1)
    
    holidays = Holiday.objects.filter(
        date__gte=current_month_start,
        date__lt=month_after
    ).prefetch_related('countries', 'categories').order_by('date')
    
    holidays = apply_filters(request, holidays)
    
    saved_holiday_ids = []
    if request.user.is_authenticated:
        saved_holiday_ids = list(
            UserHoliday.objects.filter(user=request.user).values_list('holiday_id', flat=True)
        )
    
    context = {
        'holidays': holidays,
        'saved_holiday_ids': saved_holiday_ids,
        'current_month': current_month_start,
        'next_month': next_month,
    }
    
    if request.htmx:
        return render(request, 'holidays/partials/holiday_list.html', context)
    
    return render(request, 'holidays/month_view.html', context)

def year_view(request):
    """Full year expandable grid view"""
    year = int(request.GET.get('year', timezone.now().year))
    
    holidays = Holiday.objects.filter(
        year=year
    ).prefetch_related('countries', 'categories').order_by('date')
    
    holidays = apply_filters(request, holidays)
    
    # Group by month
    months = {}
    for holiday in holidays:
        month = holiday.date.month
        if month not in months:
            months[month] = []
        months[month].append(holiday)
    
    saved_holiday_ids = []
    if request.user.is_authenticated:
        saved_holiday_ids = list(
            UserHoliday.objects.filter(user=request.user).values_list('holiday_id', flat=True)
        )
    
    context = {
        'year': year,
        'months': months,
        'saved_holiday_ids': saved_holiday_ids,
    }
    
    if request.htmx:
        return render(request, 'holidays/partials/holiday_list.html', context)
    
    return render(request, 'holidays/year_view.html', context)

def apply_filters(request, queryset):
    """Apply search and filter parameters"""
    # Search
    search = request.GET.get('search', '').strip()
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) | 
            Q(description__icontains=search)
        )
    
    # Country filter
    country = request.GET.get('country')
    if country:
        queryset = queryset.filter(
            Q(countries__code=country) | Q(is_global=True)
        )
    
    # Category filter
    category = request.GET.get('category')
    if category:
        queryset = queryset.filter(categories__slug=category)
    
    return queryset.distinct()

@login_required
@require_POST
def add_to_calendar(request, holiday_id):
    """Add holiday to user's calendar"""
    holiday = get_object_or_404(Holiday, id=holiday_id)
    
    # Get or create user calendar
    calendar, _ = UserCalendar.objects.get_or_create(user=request.user)
    
    # Add holiday
    user_holiday, created = UserHoliday.objects.get_or_create(
        user=request.user,
        holiday=holiday,
        defaults={
            'reminder': request.POST.get('reminder', 'none')
        }
    )
    
    if request.htmx:
        return render(request, 'holidays/partials/holiday_card.html', {
            'holiday': holiday,
            'is_saved': True,
        })
    
    return JsonResponse({
        'success': True,
        'added': created,
        'message': f'Added {holiday.name} to your calendar!' if created else 'Already in your calendar'
    })

@login_required
@require_POST
def remove_from_calendar(request, holiday_id):
    """Remove holiday from user's calendar"""
    holiday = get_object_or_404(Holiday, id=holiday_id)
    
    UserHoliday.objects.filter(
        user=request.user,
        holiday=holiday
    ).delete()
    
    if request.htmx:
        return render(request, 'holidays/partials/holiday_card.html', {
            'holiday': holiday,
            'is_saved': False,
        })
    
    return JsonResponse({
        'success': True,
        'message': f'Removed {holiday.name} from your calendar'
    })