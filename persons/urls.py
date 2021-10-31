from django.urls import path

from . import views

urlpatterns = [
    path("<uuid:meeting_pk>/addatt/", views.add_attendees, name="addattendees"),
    path(
        "<uuid:meeting_pk>/editatt/<int:attendee_pk>/",
        views.edit_attendee,
        name="editattendee",
    ),
    path(
        "<uuid:meeting_pk>/delatt/<int:attendee_pk>/",
        views.delete_attendee,
        name="delattendee",
    ),
    path("functions/", views.functions, name="functions"),
    path("functions/sort/", views.sort_functions, name="sortfunctions"),
    path("functions/<int:function_pk>/edit/", views.edit_function, name="editfunction"),
    path(
        "functions/<int:function_pk>/delete/",
        views.delete_function,
        name="delfunction",
    ),
    path("<uuid:meeting_pk>/addperson/", views.add_person, name="addperson"),
    path("persons/", views.list_persons, name="persons"),
    path("persons/add/", views.add_plain_person, name="addplainperson"),
    path("persons/<int:person_pk>/edit/", views.edit_person, name="editperson"),
    path("persons/<int:person_pk>/delete/", views.delete_person, name="delperson"),
]
