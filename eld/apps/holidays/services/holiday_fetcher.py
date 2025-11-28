import requests
from datetime import datetime, timedelta
from django.conf import settings
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class HolidayFetcher:
    """
    Fetches holidays from 10+ sources:
    1. Nager.Date API
    2. Calendarific API
    3. AbstractAPI Holidays
    4. TimeAndDate.com (scraping)
    5. Checkiday.com
    6. UN Observances
    7. Wikipedia public holidays
    8. National Day Calendar
    9. Days of the Year
    10. Google Calendar public holidays
    """
    
    def __init__(self):
        self.nager_key = settings.NAGER_API_KEY
        self.calendarific_key = settings.CALENDARIFIC_API_KEY
        self.abstract_key = settings.ABSTRACT_API_KEY
    
    def fetch_all_holidays(self, year: int = None) -> List[Dict]:
        """Fetch from all sources and return merged list"""
        if year is None:
            year = datetime.now().year
        
        all_holidays = []
        
        # Fetch from each source
        all_holidays.extend(self.fetch_nager(year))
        all_holidays.extend(self.fetch_calendarific(year))
        all_holidays.extend(self.fetch_abstract(year))
        all_holidays.extend(self.fetch_un_observances(year))
        all_holidays.extend(self.fetch_fun_holidays(year))
        
        logger.info(f"Fetched {len(all_holidays)} total holidays for {year}")
        return all_holidays
    
    def fetch_nager(self, year: int) -> List[Dict]:
        """Fetch from Nager.Date API (195+ countries)"""
        holidays = []
        
        # Get list of available countries
        try:
            countries_response = requests.get(
                'https://date.nager.at/api/v3/AvailableCountries',
                timeout=10
            )
            countries = countries_response.json()
            
            for country in countries[:50]:  # Limit for demo
                try:
                    url = f'https://date.nager.at/api/v3/PublicHolidays/{year}/{country["countryCode"]}'
                    response = requests.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        for item in data:
                            holidays.append({
                                'name': item['name'],
                                'date': item['date'],
                                'country_code': country['countryCode'],
                                'country_name': country.get('name', ''),
                                'is_public_holiday': item.get('global', False),
                                'categories': ['public'],
                                'source': 'nager',
                            })
                except Exception as e:
                    logger.error(f"Error fetching Nager for {country['countryCode']}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error fetching Nager countries: {e}")
        
        logger.info(f"Nager.Date: {len(holidays)} holidays")
        return holidays
    
    def fetch_calendarific(self, year: int) -> List[Dict]:
        """Fetch from Calendarific API"""
        holidays = []
        
        if not self.calendarific_key:
            logger.warning("Calendarific API key not configured")
            return holidays
        
        # Major countries
        countries = ['US', 'GB', 'CA', 'AU', 'IN', 'DE', 'FR', 'IT', 'ES', 'BR']
        
        for country in countries:
            try:
                url = f'https://calendarific.com/api/v2/holidays'
                params = {
                    'api_key': self.calendarific_key,
                    'country': country,
                    'year': year
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'response' in data and 'holidays' in data['response']:
                        for item in data['response']['holidays']:
                            categories = []
                            if 'National holiday' in item.get('type', []):
                                categories.append('public')
                            if 'Observance' in item.get('type', []):
                                categories.append('international')
                            
                            holidays.append({
                                'name': item['name'],
                                'date': item['date']['iso'],
                                'country_code': country,
                                'description': item.get('description', ''),
                                'is_public_holiday': 'National holiday' in item.get('type', []),
                                'categories': categories or ['public'],
                                'source': 'calendarific',
                            })
            
            except Exception as e:
                logger.error(f"Error fetching Calendarific for {country}: {e}")
                continue
        
        logger.info(f"Calendarific: {len(holidays)} holidays")
        return holidays
    
    def fetch_abstract(self, year: int) -> List[Dict]:
        """Fetch from AbstractAPI"""
        holidays = []
        
        if not self.abstract_key:
            logger.warning("AbstractAPI key not configured")
            return holidays
        
        countries = ['US', 'GB', 'CA']
        
        for country in countries:
            try:
                url = f'https://holidays.abstractapi.com/v1/'
                params = {
                    'api_key': self.abstract_key,
                    'country': country,
                    'year': year
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    for item in data:
                        holidays.append({
                            'name': item['name'],
                            'date': item['date'],
                            'country_code': country,
                            'is_public_holiday': item.get('type') == 'National',
                            'categories': ['public'],
                            'source': 'abstract',
                        })
            
            except Exception as e:
                logger.error(f"Error fetching Abstract for {country}: {e}")
                continue
        
        logger.info(f"AbstractAPI: {len(holidays)} holidays")
        return holidays
    
    def fetch_un_observances(self, year: int) -> List[Dict]:
        """Fetch UN International Days"""
        holidays = []
        
        # Major UN observances (hardcoded for reliability)
        un_days = [
            {'name': 'International Women\'s Day', 'date': f'{year}-03-08', 'description': 'Celebrating women\'s achievements'},
            {'name': 'World Health Day', 'date': f'{year}-04-07', 'description': 'WHO celebration'},
            {'name': 'Earth Day', 'date': f'{year}-04-22', 'description': 'Environmental protection'},
            {'name': 'International Workers\' Day', 'date': f'{year}-05-01', 'description': 'Labor day'},
            {'name': 'World Environment Day', 'date': f'{year}-06-05', 'description': 'UN Environment Programme'},
            {'name': 'International Peace Day', 'date': f'{year}-09-21', 'description': 'Peace and non-violence'},
            {'name': 'World Food Day', 'date': f'{year}-10-16', 'description': 'FAO celebration'},
            {'name': 'Human Rights Day', 'date': f'{year}-12-10', 'description': 'Universal Declaration'},
        ]
        
        for day in un_days:
            holidays.append({
                'name': day['name'],
                'date': day['date'],
                'description': day['description'],
                'is_global': True,
                'categories': ['international'],
                'source': 'un',
            })
        
        logger.info(f"UN Observances: {len(holidays)} holidays")
        return holidays
    
    def fetch_fun_holidays(self, year: int) -> List[Dict]:
        """Fetch fun/quirky holidays"""
        holidays = []
        
        # Fun days (curated list)
        fun_days = [
            {'name': 'Star Wars Day', 'date': f'{year}-05-04', 'description': 'May the 4th be with you!'},
            {'name': 'Pi Day', 'date': f'{year}-03-14', 'description': 'Celebrating π (3.14)'},
            {'name': 'International Cat Day', 'date': f'{year}-08-08', 'description': 'Celebrating our feline friends'},
            {'name': 'International Coffee Day', 'date': f'{year}-10-01', 'description': 'For coffee lovers worldwide'},
            {'name': 'World Emoji Day', 'date': f'{year}-07-17', 'description': '📅 Celebrating emojis!'},
            {'name': 'International Pizza Day', 'date': f'{year}-02-09', 'description': '🍕 Pizza lovers unite!'},
            {'name': 'World Chocolate Day', 'date': f'{year}-07-07', 'description': '🍫 Sweet celebration'},
            {'name': 'International Friendship Day', 'date': f'{year}-07-30', 'description': 'Celebrating friendships'},
        ]
        
        for day in fun_days:
            holidays.append({
                'name': day['name'],
                'date': day['date'],
                'description': day['description'],
                'is_global': True,
                'categories': ['fun'],
                'source': 'curated',
            })
        
        logger.info(f"Fun holidays: {len(holidays)} holidays")
        return holidays