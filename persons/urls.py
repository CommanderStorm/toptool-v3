from django.urls import include, path

from . import views

# app_name = "persons"
urlpatterns = [
    path(
        "functions/",
        include(
            [
                path("edit/<int:function_pk>/", views.edit_function, name="editfunction"),
                path("delete/<int:function_pk>/", views.delete_function, name="delfunction"),
                path("manage/<str:mt_pk>/", views.manage_functions, name="functions"),
                path("sort/<str:mt_pk>/", views.sort_functions, name="sortfunctions"),
            ],
        ),
    ),
    path(
        "meeting/",
        include(
            [
                path("addatt/<uuid:meeting_pk>/", views.add_attendees, name="addattendees"),
                path("addperson/<uuid:meeting_pk>/", views.add_person, name="addperson"),
                path("editatt/<int:attendee_pk>/", views.edit_attendee, name="editattendee"),
                path("delatt/<int:attendee_pk>/", views.delete_attendee, name="delattendee"),
            ],
        ),
    ),
    path("list/<str:mt_pk>/", views.list_persons, name="persons"),
    path("delete/<int:person_pk>/", views.delete_person, name="delperson"),
    path("add/<str:mt_pk>/", views.add_plain_person, name="addplainperson"),
    path("edit/<str:mt_pk>/<int:person_pk>/", views.edit_person, name="editperson"),
]
