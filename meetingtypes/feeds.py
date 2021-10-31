import datetime
from uuid import UUID

from django.core.handlers.wsgi import WSGIRequest
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django_ical.views import ICalFeed

from .models import MeetingType


# pylint: disable=no-self-use
# pylint: disable=arguments-differ
class MeetingFeed(ICalFeed):
    def get_object(
        self,
        request: WSGIRequest,
        mt_pk: str,
        ical_key: UUID,
    ) -> MeetingType:
        if not ical_key:
            raise Http404
        obj: MeetingType = get_object_or_404(MeetingType, pk=mt_pk, ical_key=ical_key)
        return obj

    def product_id(self, obj):
        return f"-//fs.tum.de//meetings//{obj.id}"

    def file_name(self, obj):
        return f"{obj.id}.ics"

    def items(self, obj):
        reference_time = timezone.now() - datetime.timedelta(days=7 * 6)
        return obj.meeting_set.filter(time__gte=reference_time).order_by("-time")

    def item_title(self, item):
        return item.get_title()

    def item_description(self, item):
        return ""

    def item_link(self, item):
        return reverse("viewmeeting", args=[item.meetingtype.id, item.id])

    def item_start_datetime(self, item):
        return item.time

    def item_end_datetime(self, item):
        return item.time + datetime.timedelta(hours=2)

    def item_location(self, item):
        return item.room
