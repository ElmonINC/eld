from django.db import models
from django.utils.text import slugify
from django.contrib.postgres.fields import ArrayField

class Country(models.Model):
    """Country model with ISO codes and flags"""
    code = models.CharField(max_length=2, unique=True, db_index=True)
    name = models.CharField(max_length=100, choices=None, db_index=True)
    flag_emoji = models.CharField(max_length=10, blank=True)
    region = models.CharField(max_length=50, blank=True)
    
    class Meta:
        verbose_name_plural = "Countries"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.flag_emoji} {self.name}"

class HolidayCategory(models.Model):
    """Categories: Public Holiday, Religious, International, Fun/Quirky, Seasonal"""
    CATEGORY_CHOICES = [
        ('public', 'Public Holiday'),
        ('religious', 'Religious'),
        ('international', 'International'),
        ('fun', 'Fun/Quirky'),
        ('seasonal', 'Seasonal'),
    ]
    
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    category_type = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    color = models.CharField(max_length=7, default='#3B82F6')  # Tailwind blue-500
    icon = models.CharField(max_length=50, blank=True)
    
    class Meta:
        verbose_name_plural = "Holiday Categories"
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Holiday(models.Model):
    """Master holiday model with rich metadata"""
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=250, blank=True)
    description = models.TextField(blank=True)
    
    # Date information
    date = models.DateField(db_index=True)
    year = models.IntegerField(db_index=True)
    is_recurring = models.BooleanField(default=True)
    
    # Location
    countries = models.ManyToManyField(Country, blank=True, related_name='holidays')
    is_global = models.BooleanField(default=False)
    
    # Categorization
    categories = models.ManyToManyField(HolidayCategory, related_name='holidays')
    
    # Metadata
    is_public_holiday = models.BooleanField(default=False)
    is_bank_holiday = models.BooleanField(default=False)
    is_observance = models.BooleanField(default=False)
    
    # Lunar/Solar info
    is_lunar = models.BooleanField(default=False)
    lunar_date = models.CharField(max_length=50, blank=True)
    
    # Sources and enrichment
    sources = ArrayField(models.CharField(max_length=100), default=list, blank=True)
    external_id = models.CharField(max_length=200, blank=True, db_index=True)
    
    # Wikipedia and links
    wikipedia_url = models.URLField(blank=True)
    official_url = models.URLField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_verified = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['date', 'name']
        indexes = [
            models.Index(fields=['date', 'is_global']),
            models.Index(fields=['year', 'date']),
        ]
        unique_together = [['name', 'date', 'year']]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.date}")
        if not self.year:
            self.year = self.date.year
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.date}"
    
    @property
    def country_flags(self):
        """Return a string of country flag emojis"""
        return " ".join([c.flag_emoji for c in self.countries.all()[:5]])
    
    @property
    def category_badges(self):
        """Return list of category data for badges"""
        return [
            {'name': c.name, 'color': c.color, 'icon': c.icon}
            for c in self.categories.all()
        ]

class HolidayAlias(models.Model):
    """Alternative names for holidays (for search and deduplication)"""
    holiday = models.ForeignKey(Holiday, on_delete=models.CASCADE, related_name='aliases')
    name = models.CharField(max_length=200)
    language = models.CharField(max_length=10, default='en')
    
    class Meta:
        verbose_name_plural = "Holiday Aliases"
        unique_together = [['holiday', 'name']]
    
    def __str__(self):
        return f"{self.name} (alias for {self.holiday.name})"