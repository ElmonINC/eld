from django.contrib import admin
from apps.calendars.models import UserCalendar, UserHoliday

@admin.register(UserCalendar)
class UserCalendarAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'timezone', 'is_public', 'created_at']
    search_fields = ['user__email', 'name']
    list_filter = ['is_public', 'created_at']
    readonly_fields = ['feed_token', 'feed_url', 'ics_url', 'created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user', 'name')
        }),
        ('Settings', {
            'fields': ('timezone', 'is_public')
        }),
        ('Feed URLs', {
            'fields': ('feed_token', 'feed_url', 'ics_url'),
            'description': 'These URLs are auto-generated and unique per user'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(UserHoliday)
class UserHolidayAdmin(admin.ModelAdmin):
    list_display = ['user', 'holiday', 'reminder', 'added_at']
    search_fields = ['user__email', 'holiday__name']
    list_filter = ['reminder', 'added_at']
    autocomplete_fields = ['user', 'holiday']
    readonly_fields = ['added_at']
    
    fieldsets = (
        ('Relationship', {
            'fields': ('user', 'holiday')
        }),
        ('Settings', {
            'fields': ('reminder', 'reminder_sent', 'notes')
        }),
        ('Metadata', {
            'fields': ('added_at',)
        }),
    )