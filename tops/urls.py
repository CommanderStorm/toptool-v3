from django.urls import include, path

from toptool.views import next_view

from . import views

# app_name = "tops"
urlpatterns = [
    path(
        "top/",
        include(
            [
                path("add/<uuid:meeting_pk>/", views.add_top, name="add_top"),
                path("edit/<uuid:top_pk>/", views.edit_top, name="edit_top"),
                path("delete/<uuid:top_pk>/", views.del_top, name="del_top"),
                path("attachment/<uuid:top_pk>/", views.show_attachment, name="show_attachment"),
            ],
        ),
    ),
    path(
        "tops/",
        include(
            [
                path("view/<uuid:meeting_pk>/", views.view_tops, name="view_tops"),
                path("sort/<uuid:meeting_pk>/", views.sort_tops, name="sort_tops"),
                path("list/<uuid:meeting_pk>/", views.list_tops, name="list_tops"),
            ],
        ),
    ),
    path(
        "next/",
        include(
            [
                path("listtops/<str:mt_pk>/", next_view("list_tops"), name="next_list_tops"),
                path("addtop/<str:mt_pk>/", next_view("add_top"), name="next_add_top"),
                path(
                    "nonexistant/<str:mt_pk>/",
                    views.next_meeting_nonexistant,
                    name="next_meeting_nonexistant",
                ),
            ],
        ),
    ),
    path(
        "stdtops/",
        include(
            [
                path("list/<str:mt_pk>/", views.list_stdtops, name="list_stdtops"),
                path("sort/<str:mt_pk>/", views.sort_stdtops, name="sort_stdtops"),
                path("add/<str:mt_pk>/", views.add_stdtop, name="add_stdtop"),
                path("edit/<uuid:top_pk>/", views.edit_stdtop, name="edit_stdtops"),
                path("delete/<uuid:top_pk>/", views.del_stdtop, name="del_stdtops"),
            ],
        ),
    ),
]
