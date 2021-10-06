import datetime

from django.contrib import messages
from django.template import defaultfilters
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from meetingtypes.models import MeetingType
from meetings.models import Meeting

class UpcomingMeetingsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.add_message(request)
        response = self.get_response(request)
        return response

    def add_message(self, request):
        now = timezone.now()
        today = now.date()
        tomorrow = today + datetime.timedelta(days=1)
        if request.session.get('got_today_message', None) == today.ctime():
            return

        meetingtype_keys = [mt.pk for mt in MeetingType.objects.all()
                            if request.user.has_perm(mt.permission())]
        try:
            meeting = Meeting.objects.filter(
                meetingtype__in=meetingtype_keys,
                time__date__in=(today, tomorrow),
                time__gt=now,
            ).earliest('time')
        except Meeting.DoesNotExist:
            return

        text = (_("Du hast heute um %(time)s eine Sitzung")
                if meeting.time.date() == today else
                _("Du hast morgen um %(time)s eine Sitzung"))
        messages.info(
            request,
            format_html(
                "{}: <a href='{}'>{}</a>",
                text % {"time": defaultfilters.time(
                    timezone.localtime(meeting.time))},
                reverse("viewmeeting", args=[
                    meeting.meetingtype.id, meeting.id,
                ]),
                meeting.get_title()
            )
        )
        request.session['got_today_message'] = today.ctime()
