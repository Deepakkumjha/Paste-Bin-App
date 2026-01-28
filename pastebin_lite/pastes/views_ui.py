from django.shortcuts import render
from django.http import Http404
from .models import Paste
from django.utils import timezone

from django.utils import timezone
from datetime import timedelta

def create_paste_ui(request):
    if request.method == "POST":
        content = request.POST.get("content")
        ttl = request.POST.get("ttl_seconds")
        max_views = request.POST.get("max_views")

        if not content:
            return render(
                request,
                "pastes/create.html",
                {"error": "Content is required"}
            )

        expires_at = None
        if ttl:
            expires_at = timezone.now() + timedelta(seconds=int(ttl))

        paste = Paste.objects.create(
            content=content,
            expires_at=expires_at,
            max_views=int(max_views) if max_views else None,
            remaining_views=int(max_views) if max_views else None,
        )

        return render(
            request,
            "pastes/create.html",
            {"paste_url": f"/p/{paste.id}"}
        )

    return render(request, "pastes/create.html")
