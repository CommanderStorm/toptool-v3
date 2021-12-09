from django.urls import path

from toptool.views import next_view

from . import views

urlpatterns = [
    path("add/", views.add, name="addmeeting"),
    path("addseries/", views.add_series, name="addmeetingseries"),
    path("next/", next_view("viewmeeting"), name="viewnextmeeting"),
    path("<uuid:meeting_pk>/", views.view_meeting, name="viewmeeting"),
    path(
        "<uuid:meeting_pk>/interactive/",
        views.interactive_tops,
        name="interactivetops",
    ),
    path("<uuid:meeting_pk>/edit/", views.edit_meeting, name="editmeeting"),
    path("<uuid:meeting_pk>/del/", views.delete_meeting, name="delmeeting"),
    path("<uuid:meeting_pk>/sendtops/", views.send_tops, name="sendtops"),
    path(
        "<uuid:meeting_pk>/sendinvitation/",
        views.send_invitation,
        name="sendinvitation",
    ),
    path(
        "<uuid:meeting_pk>/addminutetakers/",
        views.add_minute_takers,
        name="addminutetakers",
    ),
]
