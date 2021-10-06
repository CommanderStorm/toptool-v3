from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect

from meetings.models import Meeting
from meetingtypes.models import MeetingType


# simple redirect to next_view for the next meeting of the given meetingtype
# if no next meeting, redirect to view meetingtype
def next_view(next_view_name):
    def view(request: WSGIRequest, mt_pk: str) -> HttpResponse:
        meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
        try:
            next_meeting = meetingtype.next_meeting
        except Meeting.DoesNotExist:
            if next_view_name in ("listtops", "addtop"):
                return redirect('nonext', meetingtype.id)
            return redirect('viewmt', meetingtype.id)

        return redirect(next_view_name, meetingtype.id, next_meeting.id)

    return view
