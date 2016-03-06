import datetime

from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from django.utils import timezone
from django.conf import settings

from .models import Meeting
from meetingtypes.models import MeetingType
from tops.models import Top
from protokolle.models import Protokoll
from .forms import MeetingForm, MeetingSeriesForm
from toptool_common.shortcuts import render


# view single meeting (allowed only by users with permission for the
# meetingtype or allowed for public if public-bit set)
def view(request, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not meeting.meetingtype.public:          # public access disabled
        if not request.user.is_authenticated():
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        if not request.user.has_perm(meeting.meetingtype.permission()):
            return render(request, 'toptool_common/access_denied.html', {})

    tops = meeting.top_set.order_by('topid')
    attendees = meeting.attendee_set.order_by('person__name')

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
def send_invitation(request, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung):
        return render(request, 'toptool_common/access_denied.html', {})

    meeting.send_invitation(request)

    return redirect('viewmeeting', meeting.id)


# send TOPs to mailing list (allowed only by meetingtype-admin and
# sitzungsleitung)
@login_required
def send_tops(request, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung):
        return render(request, 'toptool_common/access_denied.html', {})

    meeting.send_tops(request)

    return redirect('viewmeeting', meeting.id)


# edit meeting details (allowed only by meetingtype-admin and sitzungsleitung)
@login_required
def edit(request, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung):
        return render(request, 'toptool_common/access_denied.html', {})

    initial = {
        'time': meeting.time,
        'room': meeting.room,
        'title': meeting.title,
        'topdeadline': meeting.topdeadline,
        'sitzungsleitung': meeting.sitzungsleitung,
        'protokollant': meeting.protokollant,
    }

    form = MeetingForm(request.POST or None,
                       meetingtype=meeting.meetingtype, initial=initial)
    if form.is_valid():
        Meeting.objects.filter(pk=meeting_pk).update(
            time=form.cleaned_data['time'],
            room=form.cleaned_data['room'],
            title=form.cleaned_data['title'],
            topdeadline=form.cleaned_data['topdeadline'],
            sitzungsleitung=form.cleaned_data['sitzungsleitung'],
            protokollant=form.cleaned_data['protokollant'],
        )

        return HttpResponseRedirect(reverse('viewmeeting', args=[meeting.id]))

    context = {'meeting': meeting,
               'form': form}
    return render(request, 'meetings/edit.html', context)


# edit meeting details (allowed only by meetingtype-admin)
@login_required
def delete(request, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not request.user.has_perm(meeting.meetingtype.admin_permission()):
        return render(request, 'toptool_common/access_denied.html', {})

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
        return render(request, 'toptool_common/access_denied.html', {})

    form = MeetingForm(request.POST or None, meetingtype=meetingtype)
    if form.is_valid():
        meeting = form.save()

        stdtops = list(meetingtype.standardtop_set.order_by('topid'))

        for i, stop in enumerate(stdtops):
            Top.objects.create(
                title=stop.title,
                author="",
                email="",
                description=stop.description,
                protokoll_templ=stop.protokoll_templ,
                meeting=meeting,
                topid=i+1,
            )

        if meetingtype.other_in_tops:
            Top.objects.create(
                title="Sonstiges",
                meeting=meeting,
                topid=10000,
            )

        return HttpResponseRedirect(reverse('viewmt', args=[meetingtype.id]))

    context = {'meetingtype': meetingtype,
               'form': form}
    return render(request, 'meetings/add.html', context)


# create new meetings as series (allowed only by meetingtype-admin)
@login_required
def add_series(request, mt_pk):
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    if not request.user.has_perm(meetingtype.admin_permission()):
        return render(request, 'toptool_common/access_denied.html', {})

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
