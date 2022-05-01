from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext as _

from meetings.models import Meeting
from meetingtypes.models import MeetingType
from toptool.utils.shortcuts import render


def next_view(next_view_name):
    """
    Simple redirect to next_view for the next meeting of the given meetingtype.
    If no next meeting, redirect to view meetingtype.

    @param next_view_name: method, that is being decorated
    @return next_view_name, after being wrapped in the view-decorator
    """

    def view(request: WSGIRequest, mt_pk: str) -> HttpResponse:
        """
        Simple redirect to next_view for the next meeting of the given meetingtype.
        If no next meeting, redirect to view meetingtype.

        @param request: a WSGIRequest
        @param mt_pk: id of a MeetingType
        @return: a HttpResponse
        """
        meetingtype: MeetingType = get_object_or_404(MeetingType, pk=mt_pk)
        try:
            next_meeting = meetingtype.next_meeting
        except Meeting.DoesNotExist:
            if next_view_name in ("tops:list_tops", "tops:add_top"):
                return redirect("meetingtypes:next_meeting_nonexistant", meetingtype.id)
            return redirect("meetingtypes:view_meetingtype", meetingtype.id)

        return redirect(next_view_name, meetingtype.id, next_meeting.id)

    return view


def login_failed(request: WSGIRequest) -> HttpResponse:
    """
    Displays, that the user is not allowed to log in

    @permission: allowed only by anyone
    @param request: a WSGIRequest
    @return: a possibly blank query_string
    """
    messages.error(request, _("Dir ist nicht erlaubt dich in diese Applikation einzuloggen."))
    return render(request, "base.html", {})
