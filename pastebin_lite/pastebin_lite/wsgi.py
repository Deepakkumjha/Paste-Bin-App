"""
WSGI config for pastebin_lite project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pastebin_lite.settings')

application = get_wsgi_application()
