import datetime
from uuid import UUID

from django import forms
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.handlers.wsgi import WSGIRequest
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone

from meetingtypes.models import MeetingType
from protokolle.models import Protokoll
from tops.models import Top
from toptool.forms import EmailForm
from toptool.utils.helpers import get_meeting_or_404_on_validation_error
from toptool.utils.shortcuts import render
from toptool.utils.typing import AuthWSGIRequest

from .forms import MeetingForm, MeetingSeriesForm, MinuteTakersForm
from .models import Meeting


# view single meeting (allowed only by users with permission for the
# meetingtype or allowed for public if public-bit set)
def view_meeting(request: WSGIRequest, mt_pk: str, meeting_pk: UUID) -> HttpResponse:
    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)

    if not meeting.meetingtype.public:  # public access disabled
        if not request.user.is_authenticated:
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")
        if not request.user.has_perm(meeting.meetingtype.permission()):
            raise PermissionDenied

    tops = meeting.get_tops_with_id()
    attendees = None
    if meeting.meetingtype.attendance:
        attendees = meeting.attendee_set.order_by("name")

    try:
        protokoll = meeting.protokoll
        protokoll_exists = True
    except Protokoll.DoesNotExist:
        protokoll_exists = False

    protokoll_published = protokoll_exists and protokoll.published

    protokollant_form = None
    if (
        meeting.meetingtype.protokoll
        and meeting.meetingtype.write_protokoll_button
        and not meeting.imported
        and not meeting.minute_takers.exists()
        and request.user.is_authenticated
        and request.user.has_perm(meeting.meetingtype.permission())
        and not request.user.has_perm(meeting.meetingtype.admin_permission())
        and request.user != meeting.sitzungsleitung
    ):
        protokollant_form = forms.Form(request.POST or None)
        if protokollant_form.is_valid():
            meeting.minute_takers.add(request.user)
            meeting.save()
            protokollant_form = None

    attachments = None
    if (
        meeting.meetingtype.protokoll
        and meeting.meetingtype.attachment_protokoll
        and protokoll_published
    ):
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
def interactive_tops(
    request: WSGIRequest,
    mt_pk: str,
    meeting_pk: UUID,
) -> HttpResponse:
    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)
    if not (
        request.user.has_perm(meeting.meetingtype.admin_permission())
        or request.user == meeting.sitzungsleitung
    ):
        raise PermissionDenied
    if meeting.imported:
        raise PermissionDenied

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
@login_required
def send_invitation(
    request: AuthWSGIRequest,
    mt_pk: str,
    meeting_pk: UUID,
) -> HttpResponse:
    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)

    if not (
        request.user.has_perm(meeting.meetingtype.admin_permission())
        or request.user == meeting.sitzungsleitung
    ):
        raise PermissionDenied
    if meeting.imported:  # meeting was imported
        raise PermissionDenied

    if not meeting.meetingtype.send_invitation_enabled:
        raise Http404

    subject, text, from_email, to_email = meeting.get_invitation_mail(request)

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
        return redirect("viewmeeting", meeting.meetingtype.id, meeting.id)

    context = {
        "meeting": meeting,
        "from_email": from_email,
        "to_email": to_email,
        "form": form,
    }
    return render(request, "meetings/send_invitation.html", context)


# send TOPs to mailing list (allowed only by meetingtype-admin and
# sitzungsleitung)
@login_required
def send_tops(request: AuthWSGIRequest, mt_pk: str, meeting_pk: UUID) -> HttpResponse:
    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)

    if not (
        request.user.has_perm(meeting.meetingtype.admin_permission())
        or request.user == meeting.sitzungsleitung
    ):
        raise PermissionDenied
    if meeting.imported:  # meeting was imported
        raise PermissionDenied

    if not meeting.meetingtype.send_tops_enabled:
        raise Http404

    subject, text, from_email, to_email = meeting.get_tops_mail(request)

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
        return redirect("viewmeeting", meeting.meetingtype.id, meeting.id)

    context = {
        "meeting": meeting,
        "from_email": from_email,
        "to_email": to_email,
        "form": form,
    }
    return render(request, "meetings/send_tops.html", context)


# edit meeting details (allowed only by meetingtype-admin and sitzungsleitung)
@login_required
def edit_meeting(
    request: AuthWSGIRequest,
    mt_pk: str,
    meeting_pk: UUID,
) -> HttpResponse:
    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)

    if not (
        request.user.has_perm(meeting.meetingtype.admin_permission())
        or request.user == meeting.sitzungsleitung
    ):
        raise PermissionDenied

    form = MeetingForm(
        request.POST or None,
        meetingtype=meeting.meetingtype,
        instance=meeting,
    )
    if form.is_valid():
        form.save()

        return redirect("viewmeeting", meeting.meetingtype.id, meeting.id)

    context = {
        "meeting": meeting,
        "form": form,
    }
    return render(request, "meetings/edit.html", context)


# edit meeting details (allowed only by meetingtype-admin)
@login_required
def delete_meeting(
    request: AuthWSGIRequest,
    mt_pk: str,
    meeting_pk: UUID,
) -> HttpResponse:
    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)

    if not request.user.has_perm(meeting.meetingtype.admin_permission()):
        raise PermissionDenied

    form = forms.Form(request.POST or None)
    if form.is_valid():
        meetingtype = meeting.meetingtype

        meeting.delete()

        return redirect("viewmt", meetingtype.id)

    context = {
        "meeting": meeting,
        "form": form,
    }
    return render(request, "meetings/del.html", context)


# create new meeting (allowed only by meetingtype-admin)
@login_required
def add(request: AuthWSGIRequest, mt_pk: str) -> HttpResponse:
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
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

        return redirect("viewmt", meetingtype.id)

    context = {
        "meetingtype": meetingtype,
        "form": form,
    }
    return render(request, "meetings/add.html", context)


# create new meetings as series (allowed only by meetingtype-admin)
@login_required
def add_series(request: AuthWSGIRequest, mt_pk: str) -> HttpResponse:
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
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
            deadline_delta = datetime.timedelta(hours=-1)
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

        return redirect("viewmt", meetingtype.id)

    context = {
        "meetingtype": meetingtype,
        "form": form,
    }
    return render(request, "meetings/add_series.html", context)


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


# add (further) minute takers (only allowed by meetingtype-admin, sitzungsleitung
# protokollant*innen)
@login_required
def add_minute_takers(
    request: AuthWSGIRequest,
    mt_pk: str,
    meeting_pk: UUID,
) -> HttpResponse:
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
        return redirect("viewmeeting", meeting.meetingtype.id, meeting.id)

    context = {
        "meeting": meeting,
        "form": form,
    }
    return render(request, "meetings/addminutetakers.html", context)
