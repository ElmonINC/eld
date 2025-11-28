from django.urls import path
from eld.apps.calendars import views

app_name = 'calendars'

urlpatterns = [
    path('my-calendar/', views.my_calendar, name='my_calendar'),
    path('calendar/feed/<str:feed_token>/', views.calendar_feed, name='calendar_feed'),
    path('calendar/download/', views.download_ics, name='download_ics'),
    path('calendar/bulk-add/', views.bulk_add, name='bulk_add'),
]