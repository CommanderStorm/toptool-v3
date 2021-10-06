import datetime
from uuid import UUID

from django.core.handlers.wsgi import WSGIRequest
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django_ical.views import ICalFeed

from .models import MeetingType


class MeetingFeed(ICalFeed):
    def get_object(self, request: WSGIRequest, mt_pk: str, ical_key: UUID) -> MeetingType:
        obj = get_object_or_404(MeetingType, pk=mt_pk)
        if not obj.ical_key or str(obj.ical_key) != ical_key:
            raise Http404
        return obj

    def product_id(self, obj):
        return '-//fs.tum.de//meetings//{0}'.format(obj.id)

    def file_name(self, obj):
        return '{0}.ics'.format(obj.id)

    def items(self, obj):
        reference_time = timezone.now() - datetime.timedelta(days=7*6)
        return obj.meeting_set.filter(time__gte=reference_time).order_by('-time')

    def item_title(self, item):
        return item.get_title()

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
