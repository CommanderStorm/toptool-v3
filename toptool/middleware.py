import datetime

from django.contrib import messages
from django.template import defaultfilters
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from meetings.models import Meeting
from meetingtypes.models import MeetingType


class UpcomingMeetingsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.add_message(request)
        return self.get_response(request)

    def add_message(self, request):
        now = timezone.now()
        today = now.date()
        tomorrow = today + datetime.timedelta(days=1)
        if request.session.get("got_today_message", None) == today.ctime():
            return

        meetingtype_keys = [mt.pk for mt in MeetingType.objects.all() if request.user.has_perm(mt.permission())]
        try:
            meeting = Meeting.objects.filter(
                meetingtype__in=meetingtype_keys,
                time__date__in=(today, tomorrow),
                time__gt=now,
            ).earliest("time")
        except Meeting.DoesNotExist:
            return

        meeting_message = self._generate_meeting_message(meeting, today)
        messages.info(request, meeting_message)
        request.session["got_today_message"] = today.ctime()

    @staticmethod
    def _generate_meeting_message(meeting, today):
        if meeting.time.date() == today:
            text = _("Du hast heute um %(time)s eine Sitzung")
        else:
            text = _("Du hast morgen um %(time)s eine Sitzung")
        meeting_localtime = timezone.localtime(meeting.time)
        text = text.format(time=defaultfilters.time(meeting_localtime))
        meeting_url = reverse("meetings:view_meeting", args=[meeting.id])
        return format_html(
            "{}: <a href='{}'>{}</a>",
            text,
            meeting_url,
            meeting.get_title(),
        )
