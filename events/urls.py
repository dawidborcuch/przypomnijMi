from django.urls import path
from . import views

urlpatterns = [
    path('', views.calendar_view, name='calendar'),
    path('add/', views.add_event, name='add_event'),
    path('add/<str:event_date>/', views.add_event, name='add_event_date'),
    path('edit/<int:event_id>/', views.edit_event, name='edit_event'),
    path('delete/<int:event_id>/', views.delete_event, name='delete_event'),
    path('api/events/<str:event_date>/', views.api_events_by_date, name='api_events_by_date'),
    path('api/move/<int:event_id>/', views.move_event_date, name='move_event_date'),
    path('api/upcoming/', views.api_upcoming, name='api_upcoming'),
] 