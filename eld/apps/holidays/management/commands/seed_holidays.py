from django.core.management.base import BaseCommand
from django.core.management import call_command
from datetime import datetime
from apps.holidays.tasks import refresh_holidays_for_year

class Command(BaseCommand):
    help = 'Seed initial holiday data (2025-2027) and create categories'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🎉 Starting holiday database seed...'))
        
        # Load initial fixtures (categories and countries)
        self.stdout.write('Loading categories and countries...')
        try:
            call_command('loaddata', 'initial_data')
            self.stdout.write(self.style.SUCCESS('  ✓ Loaded initial data'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ⚠ Could not load fixtures: {e}'))
            self.stdout.write('  Creating categories manually...')
            from apps.holidays.models import HolidayCategory
            categories = [
                {'name': 'Public Holiday', 'slug': 'public', 'category_type': 'public', 'color': '#3B82F6', 'icon': '🏛️'},
                {'name': 'Religious', 'slug': 'religious', 'category_type': 'religious', 'color': '#8B5CF6', 'icon': '🙏'},
                {'name': 'International Day', 'slug': 'international', 'category_type': 'international', 'color': '#10B981', 'icon': '🌍'},
                {'name': 'Fun & Quirky', 'slug': 'fun', 'category_type': 'fun', 'color': '#F59E0B', 'icon': '🎊'},
                {'name': 'Seasonal', 'slug': 'seasonal', 'category_type': 'seasonal', 'color': '#EC4899', 'icon': '🌸'},
            ]
            
            for cat_data in categories:
                cat, created = HolidayCategory.objects.get_or_create(
                    slug=cat_data['slug'],
                    defaults=cat_data
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Created category: {cat.name}'))
        
        # Seed holidays for 2025-2027
        current_year = datetime.now().year
        years = [current_year, current_year + 1, current_year + 2]
        
        total_created = 0
        total_updated = 0
        
        for year in years:
            self.stdout.write(f'\nFetching holidays for {year}...')
            created, updated = refresh_holidays_for_year(year)
            total_created += created
            total_updated += updated
            self.stdout.write(
                self.style.SUCCESS(f'  ✓ {year}: {created} created, {updated} updated')
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Seed complete! {total_created} holidays created, {total_updated} updated'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                'Run "python manage.py refresh_holidays" to update anytime'
            )
        )