from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext as _

from meetings.models import Meeting
from meetingtypes.models import MeetingType
from toptool.utils.shortcuts import render


# simple redirect to next_view for the next meeting of the given meetingtype
# if no next meeting, redirect to view meetingtype
def next_view(next_view_name):
    def view(request: WSGIRequest, mt_pk: str) -> HttpResponse:
        meetingtype: MeetingType = get_object_or_404(MeetingType, pk=mt_pk)
        try:
            next_meeting = meetingtype.next_meeting
        except Meeting.DoesNotExist:
            if next_view_name in ("list_tops", "add_top"):
                return redirect("next_meeting_nonexistant", meetingtype.id)
            return redirect("view_meetingtype", meetingtype.id)

        return redirect(next_view_name, meetingtype.id, next_meeting.id)

    return view


def login_failed(request: WSGIRequest) -> HttpResponse:
    messages.error(request, _("Dir ist nicht erlaubt dich in diese Applikation einzuloggen."))
    return render(request, "base.html", {})
