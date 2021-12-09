from django.urls import path

from . import views
from .feeds import PersonalMeetingFeed

urlpatterns = [
    path("", views.edit, name="editprofile"),
    path("sortmts/", views.sort_meetingtypes, name="sortmeetingtypes"),
    path("ical/<uuid:ical_key>/", PersonalMeetingFeed(), name="personalical"),
]
