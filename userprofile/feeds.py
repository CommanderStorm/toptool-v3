from datetime import datetime, timedelta
from uuid import UUID

from django.contrib.auth.models import User  # pylint: disable=imported-auth-user
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django_ical.views import ICalFeed

from meetings.models import Meeting
from toptool.utils.shortcuts import get_permitted_mts

from .models import Profile


# pylint: disable=no-self-use
# pylint: disable=arguments-differ
class PersonalMeetingFeed(ICalFeed):
    file_name = "meetings.ics"

    def get_object(self, request: WSGIRequest, ical_key: UUID) -> User:
        """
        This method is called to get the object for which the feed is generated.
        @param request: The request object
        @param ical_key: The
        @return:
        """
        profile: Profile = get_object_or_404(Profile, ical_key=ical_key)
        return profile.user

    def product_id(self, user: User) -> str:
        """
        This is the product identifier for the feed.
        @param user: the user for which the feed is generated
        @return: the product identifier
        """
        return f"-//fs.tum.de//meetings//user//{user.username}"

    def items(self, user: User) -> QuerySet[Meeting]:
        """
        This method is called to get the items for the feed.
        @param user: The user for which the feed is generated
        @return: a queryset of meetings
        """
        mts_with_perm = get_permitted_mts(user)
        reference_time = timezone.now() - timedelta(days=7 * 6)
        return Meeting.objects.filter(meetingtype__in=mts_with_perm, time__gte=reference_time).order_by("-time")

    def item_title(self, item: Meeting) -> str:
        """
        This method is called to get the title of the item.
        @param item: a meeting
        @return: the title of the meeting
        """
        title = item.get_title()
        if title != item.meetingtype.name:
            return f"{item.get_title()} ({item.meetingtype.name})"
        return title

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

    def item_start_datetime(self, item: Meeting) -> datetime:
        """
        This method is called to get the start datetime of the meeting.
        @param item: a meeting
        @return: the start datetime of the meeting
        """
        return item.time

    def item_end_datetime(self, item: Meeting) -> datetime:
        """
        This method is called to get the end datetime of the meeting.
        @param item: a meeting
        @return: the end datetime of the meeting
        """
        return item.time + timedelta(hours=2)

    def item_location(self, item: Meeting) -> str:
        """
        This method is called to get the location of the meeting.
        @param item: a meeting
        @return: the location of the meeting
        """
        return item.room
