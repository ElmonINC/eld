from django.core.management.base import BaseCommand
from apps.holidays.tasks import refresh_all_holidays

class Command(BaseCommand):
    help = 'Refresh all holiday data from external sources'

    def add_arguments(self, parser):
        parser.add_argument(
            '--year',
            type=int,
            help='Specific year to refresh (default: current + next 2 years)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting holiday refresh...'))
        
        if options['year']:
            from apps.holidays.tasks import refresh_holidays_for_year
            created, updated = refresh_holidays_for_year(options['year'])
            self.stdout.write(
                self.style.SUCCESS(
                    f'Year {options["year"]}: {created} created, {updated} updated'
                )
            )
        else:
            result = refresh_all_holidays()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Complete: {result["created"]} created, {result["updated"]} updated'
                )
            )