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

from .models import Paste
from .serializers import PasteCreateSerializer, PasteResponseSerializer, PasteDetailSerializer
from .utils import get_current_time


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
    """
    Create a new paste.
    POST /api/pastes → create paste (content required, optional ttl_seconds, max_views)
    """
    serializer = PasteCreateSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {
                'error': True,
                'message': get_validation_errors(serializer.errors),
                'details': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    validated_data = serializer.validated_data
    current_time = get_current_time(request)
    
    # Create paste
    paste = Paste(
        content=validated_data['content'],
        created_at=current_time
    )
    
    # Handle TTL
    ttl_seconds = validated_data.get('ttl_seconds')
    if ttl_seconds:
        paste.expires_at = current_time + timedelta(seconds=ttl_seconds)
    
    # Handle max views
    max_views = validated_data.get('max_views')
    if max_views:
        paste.max_views = max_views
        paste.remaining_views = max_views
    
    paste.save()
    
    response_serializer = PasteResponseSerializer(paste)
    return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_paste(request, paste_id):
    """
    Get a paste by ID. This counts as a view.
    GET /api/pastes/<id> → returns content, remaining_views, expires_at
    """
    current_time = get_current_time(request)
    
    try:
        paste = Paste.objects.get(pk=paste_id)
    except (Paste.DoesNotExist, ValueError):
        return Response(
            {'error': True, 'message': 'Paste not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if expired before viewing
    if paste.is_expired(current_time):
        return Response(
            {'error': True, 'message': 'Paste not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Decrement view count (this view counts)
    paste.decrement_views()
    
    serializer = PasteDetailSerializer(paste)
    return Response(serializer.data, status=status.HTTP_200_OK)


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
