import datetime
from uuid import UUID

from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django_ical.views import ICalFeed

from meetings.models import Meeting

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
        """
        Return the MeetingType object for a feed with the given key.
        @param request: a WSGIRequest object
        @param mt_pk: the primary key of the MeetingType object
        @param ical_key: an uuid for the feed (an arguably insecure "password")
        @return: the MeetingType requested if it exists, otherwise a 404
        """
        if not ical_key:
            raise Http404
        obj: MeetingType = get_object_or_404(MeetingType, pk=mt_pk, ical_key=ical_key)
        return obj

    def product_id(self, obj: MeetingType) -> str:
        """
        Return the product id for this feed.
        @param obj: the MeetingType object
        @return: the product id
        """
        return f"-//fs.tum.de//meetings//{obj.id}"

    def file_name(self, obj: MeetingType) -> str:
        """
        Return the file name for this feed.
        @param obj: the MeetingType object
        @return: the file name
        """
        return f"{obj.id}.ics"

    def items(self, obj: MeetingType) -> QuerySet[Meeting]:
        """
        Return the items for this feed.
        @param obj: the MeetingType object
        @return: a QuerySet of Meeting objects
        """
        reference_time = timezone.now() - datetime.timedelta(days=7 * 6)
        return obj.meeting_set.filter(time__gte=reference_time).order_by("-time")

    def item_title(self, item: Meeting) -> str:
        """
        Return the title for this Meeting.
        @param item: a Meeting object
        @return: the title for this Meeting
        """
        return item.get_title()

    def item_description(self, item: Meeting) -> str:
        """
        This method is called to get the description of the meeting.
        @param item: a meeting
        @return: the description of the meeting
        """
        if item.sitzungsleitung:
            return f"Sitzungsleitung: {item.sitzungsleitung}"
        return "Keine Sitzungsleitung bestimmt"

    def item_link(self, item: Meeting) -> str:
        """
        This method is called to get the link of the meeting in the meetingtool.
        @param item: a meeting
        @return: the link of the meeting in the meetingtool
        """
        return reverse("meetings:view_meeting", args=[item.id])

    def item_start_datetime(self, item: Meeting) -> datetime.datetime:
        """
        This method is called to get the start datetime of the meeting.
        @param item: a meeting
        @return: the start datetime of the meeting
        """
        return item.time

    def item_end_datetime(self, item: Meeting) -> datetime.datetime:
        """
        This method is called to get the end datetime of the meeting.
        @param item: a meeting
        @return: the end datetime of the meeting
        """
        return item.time + datetime.timedelta(hours=2)

    def item_location(self, item: Meeting) -> str:
        """
        This method is called to get the location of the meeting.
        @param item: a meeting
        @return: the location of the meeting
        """
        return item.room
