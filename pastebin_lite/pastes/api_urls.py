"""
API URL configuration for the pastes app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('healthz', views.health_check, name='health_check'),
    path('pastes', views.create_paste, name='create_paste'),
    path('pastes/<uuid:paste_id>', views.get_paste, name='get_paste'),
]
