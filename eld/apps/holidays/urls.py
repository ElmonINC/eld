from django.urls import path
from eld.apps.holidays import views

app_name = 'holidays'

urlpatterns = [
    path('discover/', views.discovery_view, name='discovery'),
    path('discover/week/', views.week_view, name='week_view'),
    path('discover/month/', views.month_view, name='month_view'),
    path('discover/year/', views.year_view, name='year_view'),
    path('holiday/<int:holiday_id>/add/', views.add_to_calendar, name='add_to_calendar'),
    path('holiday/<int:holiday_id>/remove/', views.remove_from_calendar, name='remove_from_calendar'),
]