"""
Utility functions for the pastes app.
"""
from datetime import datetime, timezone as dt_timezone
from django.conf import settings
from django.utils import timezone
import os


def get_current_time(request=None):
    """
    Get the current time, supporting TEST_MODE with x-test-now-ms header.
    """
    if settings.TEST_MODE and request is not None:
        test_now_ms = request.headers.get('x-test-now-ms') or request.META.get('HTTP_X_TEST_NOW_MS')
        if test_now_ms:
            try:
                timestamp_ms = int(test_now_ms)
                return datetime.fromtimestamp(timestamp_ms / 1000.0, tz=dt_timezone.utc)
            except (ValueError, TypeError, OSError):
                pass
    
    return timezone.now()



def get_now(request):
    if os.environ.get("TEST_MODE") == "1" and request.headers.get("x-test-now-ms"):
        return timezone.datetime.fromtimestamp(
            int(request.headers["x-test-now-ms"]) / 1000,
            tz=timezone.get_current_timezone()
        )
    return timezone.now()
