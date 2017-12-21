from django.conf.urls import url

from . import views

urlpatterns = [
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/protokoll/(?P<filetype>(html|pdf|txt))/$',
       views.show_protokoll, name="protokoll"),
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/template/(?:(?P<newline_style>win)/)?$',
       views.template, name="template"),
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/templatefilled/(?:(?P<newline_style>win)/)?$',
       views.template_filled, name="templatefilled"),
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/editprotokoll/$', views.edit_protokoll,
       name="editprotokoll"),
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/pad/$', views.pad,
       name="pad"),
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/delprotokoll/$', views.delete_protokoll,
       name="delprotokoll"),
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/protokollsuccess/$',
       views.success_protokoll, name="successprotokoll"),
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/sendprotokoll/$', views.send_protokoll,
       name="sendprotokoll"),
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/attachments/$', views.attachments,
       name="attachments"),
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/attachments/sort/$',
       views.sort_attachments, name="sortattachments"),
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/attachments/(?P<attachment_pk>[0-9]+)/$',
       views.show_attachment, name="showattachment_protokoll"),
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/attachments/(?P<attachment_pk>[0-9]+)/edit/$',
       views.edit_attachment, name="editattachment"),
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/attachments/(?P<attachment_pk>[0-9]+)/delete/$',
       views.delete_attachment, name="deleteattachment"),
]
