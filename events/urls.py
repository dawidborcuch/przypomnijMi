from django.urls import path
from . import views

urlpatterns = [
    path('', views.calendar_view, name='calendar'),
    path('add/', views.add_event, name='add_event'),
    path('add/<str:event_date>/', views.add_event, name='add_event_date'),
    path('edit/<int:event_id>/', views.edit_event, name='edit_event'),
    path('delete/<int:event_id>/', views.delete_event, name='delete_event'),
    path('api/events/<str:event_date>/', views.api_events_by_date, name='api_events_by_date'),
] 