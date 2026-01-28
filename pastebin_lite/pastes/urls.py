from django.urls import path
from .views_ui import create_paste_ui
from .views_html import view_paste_html

urlpatterns = [
    path("", create_paste_ui),
    path("<str:id>/", view_paste_html),
]
