from celery import shared_task
from django.utils import timezone
from datetime import datetime
import logging

from eld.apps.holidays.services.holiday_fetcher import HolidayFetcher
from eld.apps.holidays.services.deduplicator import HolidayDeduplicator
from eld.apps.holidays.models import Holiday, Country, HolidayCategory

logger = logging.getLogger(__name__)

@shared_task
def refresh_all_holidays():
    """
    Daily task to refresh holiday data from all sources
    Fetches current year + next 2 years
    """
    current_year = datetime.now().year
    years = [current_year, current_year + 1, current_year + 2]
    
    total_created = 0
    total_updated = 0
    
    for year in years:
        created, updated = refresh_holidays_for_year(year)
        total_created += created
        total_updated += updated
    
    logger.info(f"Holiday refresh complete: {total_created} created, {total_updated} updated")
    return {'created': total_created, 'updated': total_updated}

def refresh_holidays_for_year(year: int):
    """Refresh holidays for a specific year"""
    fetcher = HolidayFetcher()
    deduplicator = HolidayDeduplicator()
    
    # Fetch from all sources
    logger.info(f"Fetching holidays for {year}...")
    raw_holidays = fetcher.fetch_all_holidays(year)
    
    # Deduplicate
    logger.info(f"Deduplicating {len(raw_holidays)} holidays...")
    unique_holidays = deduplicator.deduplicate(raw_holidays)
    
    # Save to database
    logger.info(f"Saving {len(unique_holidays)} holidays to database...")
    created_count = 0
    updated_count = 0
    
    for holiday_data in unique_holidays:
        created, updated = save_holiday(holiday_data)
        if created:
            created_count += 1
        if updated:
            updated_count += 1
    
    logger.info(f"Year {year}: {created_count} created, {updated_count} updated")
    return created_count, updated_count

def save_holiday(data: dict):
    """Save or update a single holiday"""
    try:
        # Parse date
        if isinstance(data['date'], str):
            date = datetime.fromisoformat(data['date'].replace('Z', '+00:00')).date()
        else:
            date = data['date']
        
        # Get or create holiday
        holiday, created = Holiday.objects.get_or_create(
            name=data['name'],
            date=date,
            year=date.year,
            defaults={
                'description': data.get('description', ''),
                'is_public_holiday': data.get('is_public_holiday', False),
                'is_global': data.get('is_global', False),
                'sources': data.get('sources', [data.get('source', '')]),
            }
        )
        
        # Update if exists
        updated = False
        if not created:
            if data.get('description') and not holiday.description:
                holiday.description = data['description']
                updated = True
            
            if data.get('source'):
                if data['source'] not in holiday.sources:
                    holiday.sources.append(data['source'])
                    updated = True
            
            if updated:
                holiday.last_verified = timezone.now()
                holiday.save()
        
        # Add countries
        if 'country_code' in data:
            country, _ = Country.objects.get_or_create(
                code=data['country_code'],
                defaults={
                    'name': data.get('country_name', data['country_code']),
                    'flag_emoji': get_flag_emoji(data['country_code'])
                }
            )
            holiday.countries.add(country)
        
        # Add categories
        if 'categories' in data:
            for cat_slug in data['categories']:
                category, _ = HolidayCategory.objects.get_or_create(
                    slug=cat_slug,
                    defaults={
                        'name': cat_slug.title(),
                        'category_type': cat_slug
                    }
                )
                holiday.categories.add(category)
        
        return created, updated
    
    except Exception as e:
        logger.error(f"Error saving holiday {data.get('name')}: {e}")
        return False, False

@shared_task
def cleanup_old_data():
    """
    Clean up old holiday data
    Runs monthly on the 1st at 3 AM
    """
    from datetime import datetime
    
    # Delete holidays older than 2 years
    cutoff_date = datetime.now().date().replace(year=datetime.now().year - 2, month=1, day=1)
    
    deleted_count = Holiday.objects.filter(
        date__lt=cutoff_date
    ).delete()[0]
    
    logger.info(f"Deleted {deleted_count} old holidays")
    return {'deleted': deleted_count}

@shared_task
def update_statistics():
    """
    Update cached statistics
    Runs every 6 hours
    """
    from django.core.cache import cache
    from django.db.models import Count
    
    # Holiday counts
    stats = {
        'total_holidays': Holiday.objects.count(),
        'total_countries': Country.objects.count(),
        'total_categories': HolidayCategory.objects.count(),
        'holidays_by_category': dict(
            Holiday.objects.values('categories__name')
            .annotate(count=Count('id'))
            .values_list('categories__name', 'count')
        ),
        'holidays_by_year': dict(
            Holiday.objects.values('year')
            .annotate(count=Count('id'))
            .values_list('year', 'count')
        ),
        'updated_at': timezone.now().isoformat(),
    }
    
    cache.set('holiday_statistics', stats, timeout=6*3600)  # 6 hours
    
    logger.info(f"Updated statistics: {stats['total_holidays']} holidays")
    return stats

def get_flag_emoji(country_code: str) -> str:
    """Convert country code to flag emoji"""
    if len(country_code) != 2:
        return '🌍'
    
    return ''.join(chr(127397 + ord(c)) for c in country_code.upper())