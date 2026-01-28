"""
Views for the pastes app.
"""
from datetime import timedelta
from django.db import connection
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import uuid
from django.utils import timezone
from .models import Paste
from .serializers import PasteCreateSerializer, PasteResponseSerializer, PasteDetailSerializer
from .utils import get_current_time, get_now


@api_view(['GET'])
def health_check(request):
    """
    Health check endpoint that verifies database access.
    GET /api/healthz → { "ok": true }, HTTP 200
    """
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return Response({'ok': True}, status=status.HTTP_200_OK)
    except Exception:
        return Response(
            {'ok': False, 'error': 'Database connection failed'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )


@api_view(['POST'])
def create_paste(request):
    content = request.data.get("content")
    ttl_seconds = request.data.get("ttl_seconds")
    max_views = request.data.get("max_views")

    if not content or not isinstance(content, str):
        return Response({"error": "content is required"}, status=status.HTTP_400_BAD_REQUEST)

    if ttl_seconds is not None and int(ttl_seconds) < 1:
        return Response({"error": "ttl_seconds must be >= 1"}, status=status.HTTP_400_BAD_REQUEST)

    if max_views is not None and int(max_views) < 1:
        return Response({"error": "max_views must be >= 1"}, status=status.HTTP_400_BAD_REQUEST)

    expires_at = None
    if ttl_seconds:
        expires_at = timezone.now() + timezone.timedelta(seconds=int(ttl_seconds))

    paste = Paste.objects.create(
        id=uuid.uuid4(),
        content=content,
        expires_at=expires_at,
        max_views=max_views,
        remaining_views=max_views,
    )

    return Response(
        {
            "id": str(paste.id),
            "url": request.build_absolute_uri(f"/p/{paste.id}")
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
def get_paste(request, paste_id):
    try:
        paste = Paste.objects.get(id=paste_id)
    except Paste.DoesNotExist:
        return Response({"error": "Paste not found"}, status=404)

    now = get_now(request)

    if paste.expires_at and now >= paste.expires_at:
        return Response({"error": "Paste not found"}, status=404)

    if not paste.decrement_views():
        return Response({"error": "Paste not found"}, status=404)

    return Response(
        {
            "content": paste.content,
            "remaining_views": paste.remaining_views,
            "expires_at": paste.expires_at,
        },
        status=200
    )


def get_validation_errors(errors):
    """
    Convert DRF validation errors to a readable message.
    """
    messages = []
    for field, error_list in errors.items():
        for error in error_list:
            messages.append(f"{field}: {error}")
    return '; '.join(messages)


class PasteHTMLView(TemplateView):
    """
    HTML view for displaying a paste.
    GET /p/<id> → HTML page showing paste content safely (escaped)
    """
    template_name = 'pastes/paste_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paste_id = kwargs.get('paste_id')
        current_time = get_current_time(self.request)
        
        try:
            paste = Paste.objects.get(pk=paste_id)
        except (Paste.DoesNotExist, ValueError):
            raise Http404("Paste not found")
        
        # Check if expired before viewing
        if paste.is_expired(current_time):
            raise Http404("Paste not found")
        
        # Decrement view count (this view counts)
        paste.decrement_views()
        
        context['paste'] = paste
        return context
