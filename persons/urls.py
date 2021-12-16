from django.urls import path

from . import views

# app_name = "persons"
urlpatterns = [
    path("functions/<int:function_pk>/edit/", views.edit_function, name="editfunction"),
    path("functions/<int:function_pk>/delete/", views.delete_function, name="delfunction"),
    path("<str:mt_pk>/functions/", views.manage_functions, name="functions"),
    path("<str:mt_pk>/functions/sort/", views.sort_functions, name="sortfunctions"),
    path("<str:mt_pk>/persons/", views.list_persons, name="persons"),
    path("<int:person_pk>/persons/delete/", views.delete_person, name="delperson"),
    path("<str:mt_pk>/persons/add/", views.add_plain_person, name="addplainperson"),
    path("<str:mt_pk>/persons/<int:person_pk>/edit/", views.edit_person, name="editperson"),
    path("<uuid:meeting_pk>/addatt/", views.add_attendees, name="addattendees"),
    path("<uuid:meeting_pk>/addperson/", views.add_person, name="addperson"),
    path("editatt/<int:attendee_pk>/", views.edit_attendee, name="editattendee"),
    path("delatt/<int:attendee_pk>/", views.delete_attendee, name="delattendee"),
]

