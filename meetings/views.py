import datetime
from typing import Optional, Tuple
from uuid import UUID

from django import forms
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.core.handlers.wsgi import WSGIRequest
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from meetingtypes.models import MeetingType
from protokolle.models import Protokoll
from tops.models import Top
from toptool.utils.helpers import get_meeting_or_404_on_validation_error
from toptool.utils.permission import auth_login_required, is_admin_sitzungsleitung, require
from toptool.utils.shortcuts import render, send_mail_form
from toptool.utils.typing import AuthWSGIRequest

from .forms import MeetingForm, MeetingSeriesForm, MinuteTakersForm
from .models import Meeting


# view single meeting (allowed only by users with permission for the
# meetingtype or allowed for public if public-bit set)
def view_meeting(request: WSGIRequest, meeting_pk: UUID) -> HttpResponse:
    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)

    if not meeting.meetingtype.public:  # public access disabled
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not request.user.has_perm(meeting.meetingtype.permission()):
            raise PermissionDenied

    tops = meeting.get_tops_with_id()
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

    attachments = None
    if meeting.meetingtype.protokoll and meeting.meetingtype.attachment_protokoll and protokoll_published:
        attachments = meeting.get_attachments_with_id()

    context = {
        "meeting": meeting,
        "tops": tops,
        "protokoll_exists": protokoll_exists,
        "protokoll_published": protokoll_published,
        "attendees": attendees,
        "attachments": attachments,
        "protokollant_form": protokollant_form,
    }
    return render(request, "meetings/view.html", context)


# interactive view for agenda (allowed only by meetingtype-admin and
# sitzungsleitung)
def interactive_tops(request: WSGIRequest, meeting_pk: UUID) -> HttpResponse:
    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)
    require(is_admin_sitzungsleitung(request, meeting))
    require(not meeting.imported)

    if not meeting.meetingtype.tops:
        raise Http404

    tops = meeting.get_tops_with_id()
    first_topid = 0
    last_topid = -1
    if tops:
        first_topid = tops[0].get_topid
        last_topid = tops[-1].get_topid

    context = {
        "meeting": meeting,
        "tops": tops,
        "first_topid": first_topid,
        "last_topid": last_topid,
    }
    return render(request, "meetings/interactive.html", context)


# send invitation to mailing list (allowed only by meetingtype-admin and
# sitzungsleitung)
@auth_login_required()
def send_invitation(request: AuthWSGIRequest, meeting_pk: UUID) -> HttpResponse:
    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)

    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or request.user == meeting.sitzungsleitung):
        raise PermissionDenied
    if meeting.imported:  # meeting was imported
        raise PermissionDenied

    if not meeting.meetingtype.send_invitation_enabled:
        raise Http404

    mail_details: Tuple[str, str, str, str] = meeting.get_invitation_mail(request)
    return send_mail_form("meetings/send_invitation.html", request, mail_details, meeting)


# send TOPs to mailing list (allowed only by meetingtype-admin and
# sitzungsleitung)
@auth_login_required()
def send_tops(request: AuthWSGIRequest, meeting_pk: UUID) -> HttpResponse:
    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)

    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or request.user == meeting.sitzungsleitung):
        raise PermissionDenied
    if meeting.imported:  # meeting was imported
        raise PermissionDenied

    if not meeting.meetingtype.send_tops_enabled:
        raise Http404

    mail_details: Tuple[str, str, str, str] = meeting.get_tops_mail(request)
    return send_mail_form("meetings/send_tops.html", request, mail_details, meeting)


# edit meeting details (allowed only by meetingtype-admin and sitzungsleitung)
@auth_login_required()
def edit_meeting(request: AuthWSGIRequest, meeting_pk: UUID) -> HttpResponse:
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


# edit meeting details (allowed only by meetingtype-admin)
@auth_login_required()
def del_meeting(request: AuthWSGIRequest, meeting_pk: UUID) -> HttpResponse:
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


# create new meeting (allowed only by meetingtype-admin)
@auth_login_required()
def add_meeting(request: AuthWSGIRequest, mt_pk: str) -> HttpResponse:
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


# create new meetings as series (allowed only by meetingtype-admin)
@auth_login_required()
def add_meetings_series(request: AuthWSGIRequest, mt_pk: str) -> HttpResponse:
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


# pylint: disable=unused-argument
# signal listener that adds stdtops when meeting is created
@receiver(post_save, sender=Meeting)
def add_stdtops_listener(sender, **kwargs):
    instance = kwargs.get("instance")
    if instance.stdtops_created:
        return  # meeting was only edited
    if not instance.meetingtype.tops:
        return

    if instance.meetingtype.standard_tops:
        stdtops = list(instance.meetingtype.standardtop_set.order_by("topid"))
        for i, stop in enumerate(stdtops):
            Top.objects.create(
                title=stop.title,
                author="",
                email="",
                description=stop.description,
                protokoll_templ=stop.protokoll_templ,
                meeting=instance,
                topid=i + 1,
            )

    if instance.meetingtype.other_in_tops:
        Top.objects.create(
            title="Sonstiges",
            author="",
            email="",
            meeting=instance,
            topid=10000,
        )

    instance.stdtops_created = True
    instance.save()


# pylint: enable=unused-argument

# add (further) minute takers (only allowed by meetingtype-admin, sitzungsleitung
# protokollant*innen)
@auth_login_required()
def add_minute_takers(request: AuthWSGIRequest, meeting_pk: UUID) -> HttpResponse:
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
