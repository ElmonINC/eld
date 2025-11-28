import requests
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class HolidayEnricher:
    """
    Enriches holiday data with additional information:
    - Country flags
    - Wikipedia links
    - Better descriptions
    - Category classification
    """
    
    def __init__(self):
        self.flag_cache = {}
    
    def enrich(self, holiday_data: Dict) -> Dict:
        """Add enrichment data to a holiday"""
        
        # Add flag emoji
        if 'country_code' in holiday_data and not holiday_data.get('flag_emoji'):
            holiday_data['flag_emoji'] = self.get_flag_emoji(holiday_data['country_code'])
        
        # Classify categories if not set
        if not holiday_data.get('categories'):
            holiday_data['categories'] = self.classify_holiday(holiday_data)
        
        # Add Wikipedia link if possible
        if not holiday_data.get('wikipedia_url'):
            holiday_data['wikipedia_url'] = self.get_wikipedia_url(holiday_data.get('name', ''))
        
        return holiday_data
    
    def get_flag_emoji(self, country_code: str) -> str:
        """Convert country code to flag emoji"""
        if len(country_code) != 2:
            return '🌍'
        
        if country_code in self.flag_cache:
            return self.flag_cache[country_code]
        
        flag = ''.join(chr(127397 + ord(c)) for c in country_code.upper())
        self.flag_cache[country_code] = flag
        return flag
    
    def classify_holiday(self, holiday_data: Dict) -> List[str]:
        """Auto-classify holiday into categories"""
        name = holiday_data.get('name', '').lower()
        description = holiday_data.get('description', '').lower()
        categories = []
        
        # Religious keywords
        religious_keywords = ['christmas', 'easter', 'ramadan', 'eid', 'hanukkah', 'diwali', 
                             'buddha', 'prophet', 'saint', 'holy', 'religious']
        if any(keyword in name or keyword in description for keyword in religious_keywords):
            categories.append('religious')
        
        # Public holiday indicators
        if holiday_data.get('is_public_holiday') or 'national' in name or 'independence' in name:
            categories.append('public')
        
        # International days
        international_keywords = ['international', 'world', 'global', 'united nations', 'un day']
        if any(keyword in name or keyword in description for keyword in international_keywords):
            categories.append('international')
        
        # Fun/quirky days
        fun_keywords = ['day of', 'awareness', 'appreciation', 'pizza', 'coffee', 'cat', 
                       'dog', 'emoji', 'star wars', 'pi day', 'towel day']
        if any(keyword in name for keyword in fun_keywords):
            categories.append('fun')
        
        # Seasonal
        seasonal_keywords = ['spring', 'summer', 'autumn', 'fall', 'winter', 'equinox', 
                            'solstice', 'harvest']
        if any(keyword in name or keyword in description for keyword in seasonal_keywords):
            categories.append('seasonal')
        
        # Default to public if no category
        if not categories:
            categories.append('public')
        
        return categories
    
    def get_wikipedia_url(self, holiday_name: str) -> str:
        """Try to find Wikipedia URL for holiday"""
        if not holiday_name:
            return ''
        
        # Format for Wikipedia URL
        formatted_name = holiday_name.replace(' ', '_')
        potential_url = f'https://en.wikipedia.org/wiki/{formatted_name}'
        
        # We could verify with a HEAD request, but skip for performance
        # In production, you might want to verify or use Wikipedia API
        
        return potential_url
    
    def enrich_batch(self, holidays: List[Dict]) -> List[Dict]:
        """Enrich multiple holidays at once"""
        return [self.enrich(holiday) for holiday in holidays]