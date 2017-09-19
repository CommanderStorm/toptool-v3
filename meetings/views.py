import datetime

from django.shortcuts import get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from django.utils import timezone
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail

from .models import Meeting
from meetingtypes.models import MeetingType
from tops.models import Top
from protokolle.models import Protokoll
from .forms import MeetingForm, MeetingSeriesForm
from toptool_common.shortcuts import render


# view single meeting (allowed only by users with permission for the
# meetingtype or allowed for public if public-bit set)
def view(request, mt_pk, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not meeting.meetingtype.public:          # public access disabled
        if not request.user.is_authenticated():
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        if not request.user.has_perm(meeting.meetingtype.permission()):
            raise PermissionDenied

    tops = meeting.get_tops_with_id()
    attendees = None
    if meeting.meetingtype.attendance:
        attendees = meeting.attendee_set.order_by('name')

    try:
        protokoll = meeting.protokoll
        protokoll_exists = True
    except Protokoll.DoesNotExist:
        protokoll_exists = False

    context = {'meeting': meeting,
               'tops': tops,
               'protokoll_exists': protokoll_exists,
               'attendees': attendees}
    return render(request, 'meetings/view.html', context)


# send invitation to mailing list (allowed only by meetingtype-admin and
# sitzungsleitung)
@login_required
def send_invitation(request, mt_pk, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung):
        raise PermissionDenied
    if meeting.imported:    # meeting was imported
        raise PermissionDenied

    subject, text, from_email, to_email = meeting.get_invitation_mail(request)

    form = forms.Form(request.POST or None)
    if form.is_valid():
        send_mail(subject, text, from_email, [to_email], fail_silently=False)
        return redirect('viewmeeting', meeting.meetingtype.id, meeting.id)

    context = {'meeting': meeting,
               'subject': subject,
               'text': text,
               'from_email': from_email,
               'to_email': to_email,
               'form': form}
    return render(request, 'meetings/send_invitation.html', context)


# send TOPs to mailing list (allowed only by meetingtype-admin and
# sitzungsleitung)
@login_required
def send_tops(request, mt_pk, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung):
        raise PermissionDenied
    if meeting.imported:    # meeting was imported
        raise PermissionDenied

    subject, text, from_email, to_email = meeting.get_tops_mail(request)

    form = forms.Form(request.POST or None)
    if form.is_valid():
        send_mail(subject, text, from_email, [to_email], fail_silently=False)
        return redirect('viewmeeting', meeting.meetingtype.id, meeting.id)

    context = {'meeting': meeting,
               'subject': subject,
               'text': text,
               'from_email': from_email,
               'to_email': to_email,
               'form': form}
    return render(request, 'meetings/send_tops.html', context)


# edit meeting details (allowed only by meetingtype-admin and sitzungsleitung)
@login_required
def edit(request, mt_pk, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung):
        raise PermissionDenied

    form = MeetingForm(request.POST or None,
        meetingtype=meeting.meetingtype, instance=meeting)
    if form.is_valid():
        form.save()

        return redirect('viewmeeting', meeting.meetingtype.id, meeting.id)

    context = {'meeting': meeting,
               'form': form}
    return render(request, 'meetings/edit.html', context)


# edit meeting details (allowed only by meetingtype-admin)
@login_required
def delete(request, mt_pk, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not request.user.has_perm(meeting.meetingtype.admin_permission()):
        raise PermissionDenied

    form = forms.Form(request.POST or None)
    if form.is_valid():
        meetingtype = meeting.meetingtype

        meeting.delete()

        return redirect('viewmt', meetingtype.id)

    context = {'meeting': meeting,
               'form': form}
    return render(request, 'meetings/del.html', context)


# create new meeting (allowed only by meetingtype-admin)
@login_required
def add(request, mt_pk):
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    if not request.user.has_perm(meetingtype.admin_permission()):
        raise PermissionDenied

    form = MeetingForm(request.POST or None, meetingtype=meetingtype)
    if form.is_valid():
        meeting = form.save()

        return redirect('viewmt', meetingtype.id)

    context = {'meetingtype': meetingtype,
               'form': form}
    return render(request, 'meetings/add.html', context)


# create new meetings as series (allowed only by meetingtype-admin)
@login_required
def add_series(request, mt_pk):
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    if not request.user.has_perm(meetingtype.admin_permission()):
        raise PermissionDenied

    form = MeetingSeriesForm(request.POST or None)
    if form.is_valid():
        start = form.cleaned_data['start']
        end = form.cleaned_data['end']
        cycle = int(form.cleaned_data['cycle'])
        room = form.cleaned_data['room']

        meeting_times = []
        while start <= end:
            meeting_times.append(start)
            start += datetime.timedelta(days=cycle)

        for t in meeting_times:
            Meeting.objects.create(
                time=t,
                room=room,
                meetingtype=meetingtype,
            )

        return redirect('viewmt', meetingtype.id)

    context = {'meetingtype': meetingtype,
               'form': form}
    return render(request, 'meetings/add_series.html', context)


# signal listener that adds stdtops when meeting is created
@receiver(post_save, sender=Meeting)
def add_stdtops_listener(sender, **kwargs):
    instance = kwargs.get('instance')
    if instance.stdtops_created:
        return      # meeting was only edited

    stdtops = list(instance.meetingtype.standardtop_set.order_by('topid'))

    for i, stop in enumerate(stdtops):
        Top.objects.create(
            title=stop.title,
            author="",
            email="",
            description=stop.description,
            protokoll_templ=stop.protokoll_templ,
            meeting=instance,
            topid=i+1,
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
