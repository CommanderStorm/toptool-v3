import datetime

from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.http import Http404

from django_ical.views import ICalFeed

from meetings.models import Meeting
from meetingtypes.models import MeetingType
from .models import Profile

class PersonalMeetingFeed(ICalFeed):
    file_name = 'meetings.ics'

    def get_object(self, request, ical_key):
        profile = get_object_or_404(Profile, ical_key=ical_key)
        return profile.user

    def product_id(self, user):
        return '-//fs.tum.de//meetings//user//{0}'.format(user.username)

    def items(self, user):
        meetingtypes = MeetingType.objects.all().order_by('name')
        mts_with_perm = []
        for meetingtype in meetingtypes:
            if meetingtype.ical_key and user.has_perm(meetingtype.permission()):
                mts_with_perm.append(meetingtype.pk)
        reference_time = timezone.now() - datetime.timedelta(days=7*6)
        return Meeting.objects.filter(
            meetingtype__in=mts_with_perm,
            time__gte=reference_time,
        ).order_by('-time')

    def item_title(self, item):
        title = item.get_title()
        if title != item.meetingtype.name:
            return "{} ({})".format(item.get_title(), item.meetingtype.name)
        return title

    def item_description(self, item):
        return ""

    def item_link(self, item):
        return reverse('viewmeeting', args=[item.meetingtype.id, item.id])

    def item_start_datetime(self, item):
        return item.time

    def item_end_datetime(self, item):
        return item.time + datetime.timedelta(hours=2)

    def item_location(self, item):
        return item.room
