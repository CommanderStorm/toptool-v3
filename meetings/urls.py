from django.urls import path

from toptool.views import next_view

from . import views

# app_name = "meetings"
urlpatterns = [
    path("<str:mt_pk>/add/", views.add, name="addmeeting"),
    path("<str:mt_pk>/addseries/", views.add_series, name="addmeetingseries"),
    path("<str:mt_pk>/next/", next_view("viewmeeting"), name="viewnextmeeting"),
    path("<str:mt_pk>/<uuid:meeting_pk>/", views.view_meeting, name="viewmeeting"),
    path("<str:mt_pk>/<uuid:meeting_pk>/interactive/",views.interactive_tops,name="interactivetops",),
    path("<str:mt_pk>/<uuid:meeting_pk>/edit/", views.edit_meeting, name="editmeeting"),
    path("<str:mt_pk>/<uuid:meeting_pk>/del/", views.delete_meeting, name="delmeeting"),
    path("<str:mt_pk>/<uuid:meeting_pk>/sendtops/", views.send_tops, name="sendtops"),
    path("<str:mt_pk>/<uuid:meeting_pk>/sendinvitation/",views.send_invitation,name="sendinvitation"),
    path("<str:mt_pk>/<uuid:meeting_pk>/addminutetakers/",views.add_minute_takers,name="addminutetakers",),
]
