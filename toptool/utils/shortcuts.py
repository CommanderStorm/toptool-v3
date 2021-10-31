from typing import Any, Dict

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render as django_render

from meetingtypes.models import MeetingType


def render(
    request: WSGIRequest,
    template: str,
    context: Dict[str, Any],
) -> HttpResponse:
    if "meetingtype" in context:
        context["active_meetingtype"] = context["meetingtype"]
    elif "meeting" in context:
        context["active_meetingtype"] = context["meeting"].meetingtype

    if "meetingtypes" not in context and request.user.is_authenticated:
        meetingtypes = MeetingType.objects.order_by("name")
        mts_with_perm = []
        for meetingtype in meetingtypes:
            if request.user.has_perm(meetingtype.permission()):
                mts_with_perm.append(meetingtype)
        mt_preferences = {
            mtp.meetingtype.pk: mtp.sortid
            for mtp in request.user.meetingtypepreference_set.all()
        }
        if mt_preferences:
            max_sortid = max(mt_preferences.values()) + 1
        else:
            max_sortid = 1
        mts_with_perm.sort(
            key=lambda mt: (mt_preferences.get(mt.pk, max_sortid), mt.name),
        )
        context["meetingtypes"] = mts_with_perm[:3]

    return django_render(request, template, context)
