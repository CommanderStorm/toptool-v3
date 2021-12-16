from django.urls import path

from . import views

# app_name = "protokolle"
urlpatterns = [
    path("<str:mt_pk>/<uuid:meeting_pk>/protokoll/<str:filetype>/", views.show_protokoll, name="protokoll"),
    path("<uuid:meeting_pk>/protokoll/templates/", views.templates, name="templates"),
    path("<uuid:meeting_pk>/protokoll/edit/", views.edit_protokoll, name="editprotokoll"),
    path("<uuid:meeting_pk>/protokoll/pad/", views.pad, name="pad"),
    path("<uuid:meeting_pk>/protokoll/pad/delete/", views.delete_pad, name="delpad"),
    path("<uuid:meeting_pk>/protokoll/publish/", views.publish_protokoll, name="publishprotokoll"),
    path("<uuid:meeting_pk>/protokoll/publish/success/", views.publish_success, name="successpublish"),
    path("<uuid:meeting_pk>/protokoll/delete/", views.delete_protokoll, name="delprotokoll"),
    path("<uuid:meeting_pk>/protokoll/success/", views.success_protokoll, name="successprotokoll"),
    path("<uuid:meeting_pk>/protokoll/send/", views.send_protokoll, name="sendprotokoll"),
    path("<uuid:meeting_pk>/protokoll/attachments/", views.attachments, name="attachments"),
    path("<uuid:meeting_pk>/protokoll/attachments/sort/", views.sort_attachments, name="sortattachments"),
    path(
        "<uuid:meeting_pk>/protokoll/attachments/<int:attachment_pk>/",
        views.show_attachment,
        name="showattachment_protokoll",
    ),
    path(
        "<uuid:meeting_pk>/protokoll/attachments/<int:attachment_pk>/edit/",
        views.edit_attachment,
        name="editattachment",
    ),
    path(
        "<uuid:meeting_pk>/protokoll/attachments/<int:attachment_pk>/delete/",
        views.delete_attachment,
        name="deleteattachment",
    ),
]
