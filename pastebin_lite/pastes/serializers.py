"""
Serializers for the pastes app.
"""
from rest_framework import serializers
from .models import Paste


class PasteCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a new paste.
    """
    content = serializers.CharField(required=True, allow_blank=False)
    ttl_seconds = serializers.IntegerField(required=False, min_value=1, allow_null=True)
    max_views = serializers.IntegerField(required=False, min_value=1, allow_null=True)

    def validate_content(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Content cannot be empty.")
        return value


class PasteResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for paste responses.
    """
    class Meta:
        model = Paste
        fields = ['id', 'content', 'created_at', 'expires_at', 'remaining_views']


class PasteDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for paste detail view (GET).
    """
    class Meta:
        model = Paste
        fields = ['content', 'remaining_views', 'expires_at']
