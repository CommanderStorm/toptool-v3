from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from .models import Meeting

# view single meeting (allowed only by users with permission for the
# meetingtype)
# TODO: allow for public if public-bit is set
@login_required
def view(request, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not request.user.has_perm(meeting.meetingtype.permission):
        raise Http404("Access Denied")

    tops = meeting.top_set.order_by('topid')
    attendees = meeting.attendees.order_by('name')

    context = {'meeting': meeting,
               'tops': tops,
               'attendees': attendees}
    return render(request, 'meetings/view.html', context)

# send TOPs to mailing list (allowed only by meetingtype-admin and
# sitzungsleitung)
@login_required
def send_tops(request, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not request.user.has_perm(meeting.meetingtype.admin_permission) and not \
            request.user == meeting.sitzungsleitung:
        raise Http404("Access Denied")

    meeting.send_mail(request)

    return HttpResponseRedirect(reverse('viewmeeting', args=[meeting.id]))

# edit meeting details (allowed only by meetingtype-admin and sitzungsleitung)
@login_required
def edit(request, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not request.user.has_perm(meeting.meetingtype.admin_permission) and not \
            request.user == meeting.sitzungsleitung:
        raise Http404("Access Denied")
    # TODO

