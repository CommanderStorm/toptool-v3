from django.urls import include, path

from toptool.views import next_view

from . import views

# app_name = "meetings"
urlpatterns = [
    path(
        "add/",
        include(
            [
                path("<str:mt_pk>/", views.add_meeting, name="add_meeting"),
                path("series/<str:mt_pk>/", views.add_meetings_series, name="add_meetings_series"),
            ],
        ),
    ),
    path("next/<str:mt_pk>/", next_view("view_meeting"), name="next_view_meeting"),
    path("<uuid:meeting_pk>/", views.view_meeting, name="view_meeting"),
    path("<uuid:meeting_pk>/interactive/", views.interactive_tops, name="interactive_tops"),
    path("<uuid:meeting_pk>/edit/", views.edit_meeting, name="edit_meeting"),
    path("<uuid:meeting_pk>/delete/", views.delete_meeting, name="del_meeting"),
    path("<uuid:meeting_pk>/sendtops/", views.send_tops, name="send_tops"),
    path("<uuid:meeting_pk>/sendinvitation/", views.send_invitation, name="send_invitation"),
    path("<uuid:meeting_pk>/addminutetakers/", views.add_minute_takers, name="add_minutetakers"),
]
