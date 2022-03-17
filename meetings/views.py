import datetime
from typing import Optional
from uuid import UUID

from django import forms
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.core.handlers.wsgi import WSGIRequest
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from meetingtypes.models import MeetingType
from protokolle.models import Attachment, Protokoll
from toptool.utils.helpers import get_meeting_or_404_on_validation_error
from toptool.utils.permission import auth_login_required, is_admin_sitzungsleitung, require
from toptool.utils.shortcuts import render, send_mail_form
from toptool.utils.typing import AuthWSGIRequest

from .forms import MeetingForm, MeetingSeriesForm, MinuteTakersForm
from .models import Meeting


def view_meeting(request: WSGIRequest, meeting_pk: UUID) -> HttpResponse:
    """
    Shows a single meeting.

    @permission: allowed only by users with permission for the meetingtype or allowed for public if public-bit set
    @param request: a WSGIRequest
    @param meeting_pk: uuid of a Meeting
    @return: a HttpResponse
    """

    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)

    if not meeting.meetingtype.public:  # public access disabled
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not request.user.has_perm(meeting.meetingtype.permission()):
            raise PermissionDenied

    attendees = None
    if meeting.meetingtype.attendance:
        attendees = meeting.attendee_set.order_by("name")

    try:
        protokoll: Optional[Protokoll] = meeting.protokoll
        protokoll_exists = True
    except Protokoll.DoesNotExist:
        protokoll = None
        protokoll_exists = False

    protokoll_published = protokoll_exists and protokoll and protokoll.published

    protokollant_form = None
    protokoll_should_exist = (
        meeting.meetingtype.protokoll and meeting.meetingtype.write_protokoll_button and not meeting.imported
    )
    user_can_write_protokoll = (
        request.user.is_authenticated
        and request.user.has_perm(meeting.meetingtype.permission())
        and not request.user.has_perm(meeting.meetingtype.admin_permission())
        and request.user != meeting.sitzungsleitung
    )
    if protokoll_should_exist and not meeting.minute_takers.exists() and user_can_write_protokoll:
        protokollant_form = forms.Form(request.POST or None)
        if protokollant_form.is_valid():
            if request.user.is_anonymous:
                messages.error(
                    request,
                    _("Du must eingeloggt sein, um diese Aktion durchführen zu können"),
                )
                return redirect_to_login(request.get_full_path())
            meeting.minute_takers.add(request.user)
            meeting.save()
            protokollant_form = None

    attachments_with_id: Optional[list[tuple[int, Attachment]]] = None
    if meeting.meetingtype.protokoll and meeting.meetingtype.attachment_protokoll and protokoll_published:
        attachments_with_id = meeting.attachments_with_id

    context = {
        "meeting": meeting,
        "tops_with_id": meeting.tops_with_id,
        "protokoll_exists": protokoll_exists,
        "protokoll_published": protokoll_published,
        "attendees": attendees,
        "attachments_with_id": attachments_with_id,
        "protokollant_form": protokollant_form,
    }
    return render(request, "meetings/view.html", context)


def interactive_tops(request: WSGIRequest, meeting_pk: UUID) -> HttpResponse:
    """
    Interactive view of the agenda of a meeting.

    @permission: allowed only by meetingtype-admin and sitzungsleitung
    @param request: a WSGIRequest
    @param meeting_pk: uuid of a Meeting
    @return: a HttpResponse
    """

    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)
    require(is_admin_sitzungsleitung(request, meeting))
    require(not meeting.imported)

    if not meeting.meetingtype.tops:
        raise Http404

    tops_with_id = meeting.tops_with_id
    first_topid: int = 0
    last_topid: int = -1
    if tops_with_id:
        first_topid, _i = tops_with_id[0]
        last_topid, _i = tops_with_id[-1]

    context = {
        "meeting": meeting,
        "tops_with_id": tops_with_id,
        "first_topid": first_topid,
        "last_topid": last_topid,
    }
    return render(request, "meetings/interactive.html", context)


@auth_login_required()
def send_invitation(request: AuthWSGIRequest, meeting_pk: UUID) -> HttpResponse:
    """
    Sends an invitation for a given meeting to the meetingtype mailing list.

    @permission: allowed only by meetingtype-admin and sitzungsleitung
    @param request: a WSGIRequest by a logged-in user
    @param meeting_pk: uuid of a Meeting
    @return: a HttpResponse
    """

    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)

    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or request.user == meeting.sitzungsleitung):
        raise PermissionDenied
    if meeting.imported:  # meeting was imported
        raise PermissionDenied

    if not meeting.meetingtype.send_invitation_enabled:
        raise Http404

    mail_details: tuple[str, str, str, str] = meeting.get_invitation_mail(request)
    return send_mail_form("meetings/send_invitation.html", request, mail_details, meeting)


@auth_login_required()
def send_tops(request: AuthWSGIRequest, meeting_pk: UUID) -> HttpResponse:
    """
    Sends the TOPs for a given meeting to the meetingtype mailing list.

    @permission: allowed only by meetingtype-admin and sitzungsleitung
    @param request: a WSGIRequest by a logged-in user
    @param meeting_pk: uuid of a Meeting
    @return: a HttpResponse
    """

    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)

    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or request.user == meeting.sitzungsleitung):
        raise PermissionDenied
    if meeting.imported:  # meeting was imported
        raise PermissionDenied

    if not meeting.meetingtype.send_tops_enabled:
        raise Http404

    mail_details: tuple[str, str, str, str] = meeting.get_tops_mail(request)
    return send_mail_form("meetings/send_tops.html", request, mail_details, meeting)


@auth_login_required()
def edit_meeting(request: AuthWSGIRequest, meeting_pk: UUID) -> HttpResponse:
    """
    Edits the details for a given meeting.

    @permission: allowed only by meetingtype-admin and sitzungsleitung
    @param request: a WSGIRequest by a logged-in user
    @param meeting_pk: uuid of a Meeting
    @return: a HttpResponse
    """

    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)

    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or request.user == meeting.sitzungsleitung):
        raise PermissionDenied

    form = MeetingForm(
        request.POST or None,
        meetingtype=meeting.meetingtype,
        instance=meeting,
    )
    if form.is_valid():
        form.save()

        return redirect("meetings:view_meeting", meeting.id)

    context = {
        "meeting": meeting,
        "form": form,
    }
    return render(request, "meetings/edit.html", context)


@auth_login_required()
def del_meeting(request: AuthWSGIRequest, meeting_pk: UUID) -> HttpResponse:
    """
    Deletes the details for a given meeting.

    @permission: allowed only by meetingtype-admin
    @param request: a WSGIRequest by a logged-in user
    @param meeting_pk: uuid of a Meeting
    @return: a HttpResponse
    """

    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)

    if not request.user.has_perm(meeting.meetingtype.admin_permission()):
        raise PermissionDenied

    form = forms.Form(request.POST or None)
    if form.is_valid():
        meetingtype = meeting.meetingtype

        meeting.delete()

        return redirect("meetingtypes:view_meetingtype", meetingtype.id)

    context = {
        "meeting": meeting,
        "form": form,
    }
    return render(request, "meetings/del.html", context)


@auth_login_required()
def add_meeting(request: AuthWSGIRequest, mt_pk: str) -> HttpResponse:
    """
    Creates a new meeting for a meetingtype.

    @permission: allowed only by meetingtype-admin
    @param request: a WSGIRequest by a logged-in user
    @param mt_pk: id of a MeetingType
    @return: a HttpResponse
    """

    meetingtype: MeetingType = get_object_or_404(MeetingType, pk=mt_pk)
    if not request.user.has_perm(meetingtype.admin_permission()):
        raise PermissionDenied

    initial = {
        "time": timezone.localtime().replace(hour=18, minute=0, second=0),
    }
    form = MeetingForm(
        request.POST or None,
        meetingtype=meetingtype,
        initial=initial,
    )
    if form.is_valid():
        form.save()

        return redirect("meetingtypes:view_meetingtype", meetingtype.id)

    context = {
        "meetingtype": meetingtype,
        "form": form,
    }
    return render(request, "meetings/add.html", context)


@auth_login_required()
def add_meetings_series(request: AuthWSGIRequest, mt_pk: str) -> HttpResponse:
    """
    Creates new meetings for a meetingtype as a series.
    A series is a way to create meetings "en-bloc"

    @permission: allowed only by meetingtype-admin
    @param request: a WSGIRequest by a logged-in user
    @param mt_pk: id of a MeetingType
    @return: a HttpResponse
    """

    meetingtype: MeetingType = get_object_or_404(MeetingType, pk=mt_pk)
    if not request.user.has_perm(meetingtype.admin_permission()):
        raise PermissionDenied

    initial = {
        "start": timezone.localtime().replace(hour=18, minute=0, second=0),
        "end": (timezone.localtime() + datetime.timedelta(days=7)).replace(
            hour=18,
            minute=0,
            second=0,
        ),
    }
    form = MeetingSeriesForm(
        request.POST or None,
        initial=initial,
        meetingtype=meetingtype,
    )
    if form.is_valid():
        start = form.cleaned_data["start"]
        end = form.cleaned_data["end"]
        cycle = int(form.cleaned_data["cycle"])
        room = form.cleaned_data["room"]

        if not meetingtype.tops or not meetingtype.top_deadline:
            top_deadline = "no"
        else:
            top_deadline = form.cleaned_data["top_deadline"]

        if top_deadline == "hour":
            deadline_delta: Optional[datetime.timedelta] = datetime.timedelta(hours=-1)
        elif top_deadline == "day":
            deadline_delta = datetime.timedelta(days=-1)
        else:
            deadline_delta = None

        meeting_times = []
        while start <= end:
            meeting_times.append(start)
            start += datetime.timedelta(days=cycle)

        for meeting_time in meeting_times:
            Meeting.objects.create(
                time=meeting_time,
                room=room,
                meetingtype=meetingtype,
                topdeadline=(meeting_time + deadline_delta if deadline_delta else None),
            )

        return redirect("meetingtypes:view_meetingtype", meetingtype.id)

    context = {
        "meetingtype": meetingtype,
        "form": form,
    }
    return render(request, "meetings/add_series.html", context)


@auth_login_required()
def add_minute_takers(request: AuthWSGIRequest, meeting_pk: UUID) -> HttpResponse:
    """
    Adds a (further) minute taker.

    @permission: allowed only by meetingtype-admin, sitzungsleitung and protokollant*innen
    @param request: a WSGIRequest by a logged-in user
    @param meeting_pk: uuid of a Meeting
    @return: a HttpResponse
    """

    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)
    if not (
        request.user.has_perm(meeting.meetingtype.admin_permission())
        or request.user == meeting.sitzungsleitung
        or request.user in meeting.minute_takers.all()
    ):
        raise PermissionDenied

    if not meeting.meetingtype.protokoll:
        raise Http404

    form = MinuteTakersForm(
        request.POST or None,
        meetingtype=meeting.meetingtype,
        instance=meeting,
    )
    if form.is_valid():
        form.save()
        return redirect("meetings:view_meeting", meeting.id)

    context = {
        "meeting": meeting,
        "form": form,
    }
    return render(request, "meetings/addminutetakers.html", context)
