from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from django.utils import timezone

from .models import Meeting
from tops.models import Top
from protokolle.models import Protokoll
from meetingtypes.forms import MeetingAddForm
from toptool_common.shortcuts import render

# view single meeting (allowed only by users with permission for the
# meetingtype or allowed for public if public-bit set)
def view(request, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not meeting.meetingtype.public: # public access disabled
        if not request.user.is_authenticated():
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        if not request.user.has_perm(meeting.meetingtype.permission()):
            raise Http404("Access Denied")

    tops = meeting.top_set.order_by('topid')
    attendees = meeting.attendee_set.order_by('person__name')
   
    topdeadline_over = (meeting.topdeadline and
        meeting.topdeadline < timezone.now())

    try:
        protokoll = meeting.protokoll
        protokoll_exists = True
    except Protokoll.DoesNotExist:
        protokoll_exists = False

    context = {'meeting': meeting,
               'tops': tops,
               'protokoll_exists': protokoll_exists,
               'topdeadline_over': topdeadline_over,
               'attendees': attendees}
    return render(request, 'meetings/view.html', context)

# send invitation to mailing list (allowed only by meetingtype-admin and
# sitzungsleitung)
@login_required
def send_invitation(request, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not request.user.has_perm(meeting.meetingtype.admin_permission()) and not \
            request.user == meeting.sitzungsleitung:
        raise Http404("Access Denied")

    meeting.send_invitation(request)

    return redirect('viewmeeting', meeting.id)

# send TOPs to mailing list (allowed only by meetingtype-admin and
# sitzungsleitung)
@login_required
def send_tops(request, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not request.user.has_perm(meeting.meetingtype.admin_permission()) and not \
            request.user == meeting.sitzungsleitung:
        raise Http404("Access Denied")

    meeting.send_tops(request)

    return redirect('viewmeeting', meeting.id)

# edit meeting details (allowed only by meetingtype-admin and sitzungsleitung)
@login_required
def edit(request, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not request.user.has_perm(meeting.meetingtype.admin_permission()) and not \
            request.user == meeting.sitzungsleitung:
        raise Http404("Access Denied")

    initial = {
        'time': meeting.time,
        'room': meeting.room,
        'semester': meeting.semester,
        'title': meeting.title,
        'topdeadline': meeting.topdeadline,
        'sitzungsleitung': meeting.sitzungsleitung,
        'protokollant': meeting.protokollant,
    }

    form = MeetingAddForm(request.POST or None,
        meetingtype=meeting.meetingtype, initial=initial)
    if form.is_valid():
        Meeting.objects.filter(pk=meeting_pk).update(
            time=form.cleaned_data['time'],
            room=form.cleaned_data['room'],
            semester=form.cleaned_data['semester'],
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
        raise Http404("Access Denied")
    
    form = forms.Form(request.POST or None)
    if form.is_valid():
        meetingtype = meeting.meetingtype

        Top.objects.filter(meeting=meeting).delete()
        Protokoll.objects.filter(meeting=meeting).get().deleteFiles()
        Protokoll.objects.filter(meeting=meeting).delete()
        meeting.delete()

        return redirect('viewmt', meetingtype.id)

    context = {'meeting': meeting,
               'form': form}
    return render(request, 'meetings/del.html', context)


