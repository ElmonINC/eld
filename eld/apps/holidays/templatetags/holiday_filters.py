from django import template
from datetime import datetime, date
from django.utils import timezone

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    if dictionary is None:
        return None
    return dictionary.get(int(key) if isinstance(key, str) and key.isdigit() else key)

@register.filter
def days_until(target_date):
    """Calculate days until a date"""
    if isinstance(target_date, str):
        target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
    
    today = timezone.now().date()
    delta = target_date - today
    return delta.days

@register.filter
def month_name(month_number):
    """Convert month number to name"""
    try:
        month_num = int(month_number)
        return date(2000, month_num, 1).strftime('%B')
    except (ValueError, TypeError):
        return ''

@register.filter
def timeuntil_days(target_date):
    """Return number of days until date"""
    if isinstance(target_date, str):
        target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
    
    today = timezone.now().date()
    if target_date < today:
        return 0
    
    delta = target_date - today
    return delta.days

@register.simple_tag
def get_country_flag(country_code):
    """Convert country code to flag emoji"""
    if len(country_code) != 2:
        return '🌍'
    return ''.join(chr(127397 + ord(c)) for c in country_code.upper())