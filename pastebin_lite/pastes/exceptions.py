"""
Custom exception handling for the pastes app.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns JSON error responses.
    """
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            'error': True,
            'message': get_error_message(response.data),
            'status_code': response.status_code
        }
        response.data = error_data

    return response


def get_error_message(data):
    """
    Extract a human-readable error message from DRF error data.
    """
    if isinstance(data, dict):
        messages = []
        for key, value in data.items():
            if isinstance(value, list):
                messages.append(f"{key}: {', '.join(str(v) for v in value)}")
            else:
                messages.append(f"{key}: {value}")
        return '; '.join(messages)
    elif isinstance(data, list):
        return ', '.join(str(item) for item in data)
    return str(data)
