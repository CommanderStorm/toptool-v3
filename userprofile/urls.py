from django.urls import path

from . import views
from .feeds import PersonalMeetingFeed

app_name = "userprofile"
urlpatterns = [
    path("", views.edit_profile, name="edit_profile"),
    path("sortmts/", views.sort_meetingtypes, name="sort_meetingtypes"),
    path("ical/<uuid:ical_key>/", PersonalMeetingFeed(), name="personal_ical_meeting_feed"),
]
