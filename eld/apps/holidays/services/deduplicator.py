from difflib import SequenceMatcher
from datetime import datetime, timedelta
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class HolidayDeduplicator:
    """
    Deduplicates holidays from multiple sources using fuzzy matching.
    
    Handles:
    - Slight name variations (e.g., "New Year's Day" vs "New Year Day")
    - Same holiday on same date from different sources
    - Similar holidays within a date range (for lunar-based holidays)
    """
    
    # Similarity threshold (0.0-1.0)
    NAME_SIMILARITY_THRESHOLD = 0.85
    
    # Date range for fuzzy date matching (lunar holidays, etc.)
    DATE_FUZZY_RANGE_DAYS = 3
    
    def deduplicate(self, holidays: List[Dict]) -> List[Dict]:
        """
        Remove duplicate holidays using fuzzy matching.
        
        Args:
            holidays: List of holiday dicts from multiple sources
        
        Returns:
            List of deduplicated holidays with sources merged
        """
        if not holidays:
            return []
        
        # Group by date first for efficiency
        by_date = self._group_by_date(holidays)
        
        deduplicated = []
        seen_indices = set()
        
        for date, holidays_on_date in by_date.items():
            # Deduplicate within each date group
            for i, holiday in enumerate(holidays_on_date):
                if i in seen_indices:
                    continue
                
                # Find all similar holidays for this one
                similar_group = [i]
                
                for j in range(i + 1, len(holidays_on_date)):
                    if j in seen_indices:
                        continue
                    
                    if self._are_similar(holiday, holidays_on_date[j]):
                        similar_group.append(j)
                
                # Merge all similar holidays
                merged = self._merge_holidays(
                    [holidays_on_date[idx] for idx in similar_group]
                )
                deduplicated.append(merged)
                
                # Mark as seen
                seen_indices.update(similar_group)
        
        # Check for fuzzy date matches (e.g., lunar holidays)
        deduplicated = self._merge_fuzzy_dates(deduplicated)
        
        logger.info(
            f"Deduplicated {len(holidays)} holidays down to {len(deduplicated)} "
            f"({len(holidays) - len(deduplicated)} duplicates removed)"
        )
        
        return deduplicated
    
    def _group_by_date(self, holidays: List[Dict]) -> Dict[str, List[Dict]]:
        """Group holidays by date for faster comparison."""
        by_date = {}
        
        for holiday in holidays:
            date = holiday.get('date')
            if isinstance(date, str):
                # Normalize date format
                try:
                    date_obj = datetime.fromisoformat(
                        date.replace('Z', '+00:00')
                    ).date()
                    date_key = date_obj.isoformat()
                except (ValueError, AttributeError):
                    date_key = date
            else:
                date_key = date.isoformat() if hasattr(date, 'isoformat') else str(date)
            
            if date_key not in by_date:
                by_date[date_key] = []
            by_date[date_key].append(holiday)
        
        return by_date
    
    def _are_similar(self, holiday1: Dict, holiday2: Dict) -> bool:
        """
        Check if two holidays are likely duplicates.
        
        Compares names and ensures they're on the same or nearby dates.
        """
        name1 = holiday1.get('name', '').lower().strip()
        name2 = holiday2.get('name', '').lower().strip()
        
        if not name1 or not name2:
            return False
        
        # Calculate name similarity
        similarity = SequenceMatcher(None, name1, name2).ratio()
        
        if similarity < self.NAME_SIMILARITY_THRESHOLD:
            return False
        
        # Check date proximity (for lunar/moving holidays)
        if not self._dates_are_close(holiday1.get('date'), holiday2.get('date')):
            return False
        
        return True
    
    def _dates_are_close(self, date1, date2) -> bool:
        """
        Check if two dates are within fuzzy range.
        Useful for lunar-based holidays that move slightly.
        """
        try:
            # Parse dates
            d1 = self._parse_date(date1)
            d2 = self._parse_date(date2)
            
            if not d1 or not d2:
                return True  # If we can't parse, assume they could match
            
            # Check if within fuzzy range
            diff = abs((d1 - d2).days)
            return diff <= self.DATE_FUZZY_RANGE_DAYS
        
        except Exception:
            return True  # If parsing fails, be lenient
    
    def _parse_date(self, date_obj):
        """Parse various date formats."""
        if isinstance(date_obj, str):
            try:
                return datetime.fromisoformat(
                    date_obj.replace('Z', '+00:00')
                ).date()
            except (ValueError, AttributeError):
                return None
        
        if hasattr(date_obj, 'date'):  # datetime object
            return date_obj.date()
        
        if hasattr(date_obj, 'isoformat'):  # date object
            return date_obj
        
        return None
    
    def _merge_holidays(self, holidays: List[Dict]) -> Dict:
        """
        Merge multiple similar holidays into one canonical entry.
        Prefers complete data and combines sources.
        """
        if not holidays:
            return {}
        
        if len(holidays) == 1:
            return holidays[0].copy()
        
        # Start with the most complete entry
        merged = self._most_complete_holiday(holidays).copy()
        
        # Merge sources
        sources = set()
        for h in holidays:
            if isinstance(h.get('source'), str):
                sources.add(h['source'])
            elif isinstance(h.get('sources'), list):
                sources.update(h['sources'])
        
        if sources:
            merged['sources'] = list(sources)
        
        # Merge categories (union of all categories)
        categories = set()
        for h in holidays:
            if isinstance(h.get('categories'), list):
                categories.update(h['categories'])
            elif isinstance(h.get('category_type'), str):
                categories.add(h['category_type'])
        
        if categories:
            merged['categories'] = list(categories)
        
        # Prefer description with more content
        if 'description' not in merged or not merged['description']:
            for h in holidays:
                if h.get('description'):
                    merged['description'] = h['description']
                    break
        
        # Merge is_public_holiday (true if any source says it's public)
        if any(h.get('is_public_holiday') for h in holidays):
            merged['is_public_holiday'] = True
        
        # Merge is_global (true if any source marks as global)
        if any(h.get('is_global') for h in holidays):
            merged['is_global'] = True
        
        return merged
    
    def _most_complete_holiday(self, holidays: List[Dict]) -> Dict:
        """
        Find the holiday entry with the most data fields filled.
        Used as base for merging.
        """
        def completeness_score(h: Dict) -> int:
            """Count non-empty fields."""
            return sum(
                1 for value in h.values()
                if value and (not isinstance(value, list) or len(value) > 0)
            )
        
        return max(holidays, key=completeness_score)
    
    def _merge_fuzzy_dates(self, holidays: List[Dict]) -> List[Dict]:
        """
        Find holidays with slightly different dates that are likely the same
        holiday (e.g., lunar-based holidays that move 1-2 days year to year).
        """
        if not holidays:
            return holidays
        
        # Group by name and proximity
        name_groups = {}
        merged_set = set()
        result = []
        
        for idx, holiday in enumerate(holidays):
            if idx in merged_set:
                continue
            
            name = holiday.get('name', '').lower().strip()
            
            # Find holidays with same name within fuzzy date range
            similar = [idx]
            for other_idx in range(idx + 1, len(holidays)):
                if other_idx in merged_set:
                    continue
                
                other = holidays[other_idx]
                other_name = other.get('name', '').lower().strip()
                
                if name == other_name and self._dates_are_close(
                    holiday.get('date'), other.get('date')
                ):
                    similar.append(other_idx)
            
            # If we found similar entries, merge them
            if len(similar) > 1:
                merged = self._merge_holidays(
                    [holidays[i] for i in similar]
                )
                result.append(merged)
                merged_set.update(similar)
            else:
                result.append(holiday.copy())
                merged_set.add(idx)
        
        return result
