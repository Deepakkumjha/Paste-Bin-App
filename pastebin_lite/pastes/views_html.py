from . models import Paste
from django.http import Http404
from django.shortcuts import render


def view_paste_html(request, id):
    try:
        paste = Paste.objects.get(id=id)
    except Paste.DoesNotExist:
        raise Http404()

    if not paste.is_available():
        raise Http404()

    paste.register_view()

    return render(
        request,
        "pastes/view.html",
        {
            "content": paste.content,
            "remaining_views": paste.remaining_views,
            "expires_at": paste.expires_at
        }
    )
