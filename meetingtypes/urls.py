from django.urls import include, path

from . import views
from .feeds import MeetingFeed

# app_name = "meetingtypes"
urlpatterns = [
    path(
        "meetingtype/",
        include(
            [
                path("list/", views.list_meetingtypes, name="list_meetingtypes"),
                path("add/", views.add_meetingtype, name="add_meetingtype"),
                path("edit/<str:mt_pk>/", views.edit_meetingtype, name="edit_meetingtype"),
                path("delete/<str:mt_pk>/", views.del_meetingtype, name="del_meetingtype"),
            ],
        ),
    ),
    path("list/admins/", views.list_admins, name="list_admins"),
    path("overview/", views.index, name="main_overview"),
    path("<str:mt_pk>/", views.view_meetingtype, name="view_meetingtype"),
    path("<str:mt_pk>/archive/<int:year>/", views.view_archive, name="view_archive"),
    path("<str:mt_pk>/search/", views.search, name="search_meetingtype"),
    path("<str:mt_pk>/search/archive/<int:year>/", views.search_archive, name="search_archive"),
    path("<str:mt_pk>/upcoming/", views.upcoming_meetings, name="upcoming_meetings"),
    path("<str:mt_pk>/ical/<uuid:ical_key>/", MeetingFeed(), name="ical_meeting_feed"),
]
