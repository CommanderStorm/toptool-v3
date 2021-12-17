from django.urls import include, path

from . import views

# app_name = "protokolle"
urlpatterns = [
    path(
        "pad/",
        include(
            [
                path("<uuid:meeting_pk>/", views.view_pad, name="view_pad"),
                path("delete/<uuid:meeting_pk>/", views.delete_pad, name="del_pad"),
            ],
        ),
    ),
    path(
        "publish/",
        include(
            [
                path("<uuid:meeting_pk>/", views.publish_protokoll, name="publish_protokoll"),
                path("success/<uuid:meeting_pk>/", views.publish_success, name="publish_success"),
            ],
        ),
    ),
    path(
        "attachments/",
        include(
            [
                path("<uuid:meeting_pk>/", views.attachments, name="attachments"),
                path("sort/<uuid:meeting_pk>/", views.sort_attachments, name="sort_attachments"),
                path("show/<int:attachment_pk>/", views.show_attachment, name="show_attachment_protokoll"),
                path("edit/<int:attachment_pk>/", views.edit_attachment, name="edit_attachment"),
                path("delete/<int:attachment_pk>/", views.del_attachment, name="del_attachment"),
            ],
        ),
    ),
    path("show/<uuid:meeting_pk>/<str:filetype>/", views.show_protokoll, name="show_protokoll"),
    path("templates/<uuid:meeting_pk>/", views.templates, name="templates"),
    path("edit/<uuid:meeting_pk>/", views.edit_protokoll, name="edit_protokoll"),
    path("delete/<uuid:meeting_pk>/", views.delete_protokoll, name="del_protokoll"),
    path("success/<uuid:meeting_pk>/", views.success_protokoll, name="success_protokoll"),
    path("send/<uuid:meeting_pk>/", views.send_protokoll, name="send_protokoll"),
]
