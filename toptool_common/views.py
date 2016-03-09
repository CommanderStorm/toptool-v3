from django.shortcuts import get_object_or_404, redirect

from meetingtypes.models import MeetingType
from meetings.models import Meeting


# simple redirect to next_view for the next meeting of the given meetingtype
# if no next meeting, redirect to view meetingtype
def next_view(next_view_name):
    def view(request, mt_pk):
        meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
        try:
            next_meeting = meetingtype.next_meeting
        except Meeting.DoesNotExist:
            return redirect('viewmt', meetingtype.id)

        return redirect(next_view_name, meetingtype.id, next_meeting.id)

    return view
