from typing import Any, Optional

from django.contrib.auth.models import User  # pylint: disable=imported-auth-user
from django.core.handlers.wsgi import WSGIRequest
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render as django_render

from meetings.models import Meeting
from meetingtypes.models import MeetingType
from protokolle.models import Protokoll
from toptool.forms import EmailForm
from toptool.utils.typing import AuthWSGIRequest


def render(request: WSGIRequest, template: str, context: dict[str, Any]) -> HttpResponse:
    if "meetingtype" in context:
        context["active_meetingtype"] = context["meetingtype"]
    elif "meeting" in context:
        context["active_meetingtype"] = context["meeting"].meetingtype

    if "meetingtypes" not in context and request.user.is_authenticated:
        mts_with_perm = get_permitted_mts_sorted(request.user)
        context["meetingtypes"] = mts_with_perm[:3]

    return django_render(request, template, context)


def get_permitted_mts(user: User) -> list[MeetingType]:
    """
    @returns all the meetingtypes the user has access to ordered by name
    """
    meetingtypes = MeetingType.objects.order_by("name")
    mts_with_perm = []
    for meetingtype in meetingtypes:
        if user.has_perm(meetingtype.permission()):
            mts_with_perm.append(meetingtype)
    return mts_with_perm


def get_permitted_mts_sorted(user: User) -> list[MeetingType]:
    """
    @returns all the meetingtypes the user has access to ordered by user-preference and secondarily by name
    """
    mts_with_perm = get_permitted_mts(user)
    mt_preferences = {mtp.meetingtype.pk: mtp.sortid for mtp in user.meetingtypepreference_set.all()}
    if mt_preferences:
        max_sortid = max(mt_preferences.values()) + 1
    else:
        max_sortid = 1
    mts_with_perm.sort(
        key=lambda mt: (mt_preferences.get(mt.pk, max_sortid), mt.name),
    )
    return mts_with_perm


def send_mail_form(
    template_url: str,
    request: AuthWSGIRequest,
    mail_details: tuple[str, str, str, str],
    meeting: Meeting,
    protokoll: Optional[Protokoll] = None,
) -> HttpResponse:
    subject, text, from_email, to_email = mail_details
    form = EmailForm(
        request.POST or None,
        initial={
            "subject": subject,
            "text": text,
        },
    )
    if form.is_valid():
        subject = form.cleaned_data["subject"]
        text = form.cleaned_data["text"]
        send_mail(subject, text, from_email, [to_email], fail_silently=False)
        return redirect("meetings:view_meeting", meeting.id)

    context = {
        "meeting": meeting,
        "from_email": from_email,
        "to_email": to_email,
        "form": form,
    }
    if protokoll:
        context["protokoll"] = protokoll
    return render(request, template_url, context)
