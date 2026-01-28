"""
URL configuration for pastebin_lite project.
"""
from django.urls import path, include

urlpatterns = [
    path('api/', include('pastes.api_urls')),
    path('p/', include('pastes.urls')),
]
