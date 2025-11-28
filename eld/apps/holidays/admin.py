from django.contrib import admin
from apps.holidays.models import Country, HolidayCategory, Holiday, HolidayAlias

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['flag_emoji', 'name', 'code', 'region']
    search_fields = ['name', 'code']
    list_filter = ['region']
    ordering = ['name']

@admin.register(HolidayCategory)
class HolidayCategoryAdmin(admin.ModelAdmin):
    list_display = ['icon', 'name', 'category_type', 'color']
    list_filter = ['category_type']
    prepopulated_fields = {'slug': ('name',)}

class HolidayAliasInline(admin.TabularInline):
    model = HolidayAlias
    extra = 1

@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'year', 'country_flags', 'is_public_holiday', 'is_global']
    list_filter = ['year', 'is_public_holiday', 'is_global', 'is_lunar', 'categories']
    search_fields = ['name', 'description']
    filter_horizontal = ['countries', 'categories']
    date_hierarchy = 'date'
    inlines = [HolidayAliasInline]
    readonly_fields = ['created_at', 'updated_at', 'last_verified']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'date', 'year')
        }),
        ('Classification', {
            'fields': ('categories', 'is_public_holiday', 'is_bank_holiday', 'is_observance')
        }),
        ('Location', {
            'fields': ('countries', 'is_global')
        }),
        ('Lunar/Solar', {
            'fields': ('is_lunar', 'lunar_date'),
            'classes': ('collapse',)
        }),
        ('Sources & Links', {
            'fields': ('sources', 'external_id', 'wikipedia_url', 'official_url'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'last_verified'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_verified', 'mark_as_public_holiday']
    
    def mark_as_verified(self, request, queryset):
        from django.utils import timezone
        queryset.update(last_verified=timezone.now())
        self.message_user(request, f'{queryset.count()} holidays marked as verified')
    mark_as_verified.short_description = 'Mark selected holidays as verified'
    
    def mark_as_public_holiday(self, request, queryset):
        queryset.update(is_public_holiday=True)
        self.message_user(request, f'{queryset.count()} holidays marked as public holidays')
    mark_as_public_holiday.short_description = 'Mark as public holidays'