from django.urls import include, path

from . import views

# app_name = "persons"
urlpatterns = [
    path(
        "functions/",
        include(
            [
                path("edit/<int:function_pk>/", views.edit_function, name="edit_function"),
                path("delete/<int:function_pk>/", views.del_function, name="del_function"),
                path("manage/<str:mt_pk>/", views.manage_functions, name="manage_functions"),
                path("sort/<str:mt_pk>/", views.sort_functions, name="sort_functions"),
            ],
        ),
    ),
    path(
        "meeting/",
        include(
            [
                path(
                    "add/",
                    include(
                        [
                            path("attendees/<uuid:meeting_pk>/", views.add_attendees, name="add_attendees"),
                            path("person/<uuid:meeting_pk>/", views.add_person, name="add_person"),
                        ],
                    ),
                ),
                path("editatt/<int:attendee_pk>/", views.edit_attendee, name="edit_attendee"),
                path("delatt/<int:attendee_pk>/", views.delete_attendee, name="del_attendee"),
            ],
        ),
    ),
    path("list/<str:mt_pk>/", views.list_persons, name="list_persons"),
    path("delete/<int:person_pk>/", views.del_person, name="del_person"),
    path("add/<str:mt_pk>/", views.add_plain_person, name="add_plain_person"),
    path("edit/<str:mt_pk>/<int:person_pk>/", views.edit_person, name="edit_person"),
]
