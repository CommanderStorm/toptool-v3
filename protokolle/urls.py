from django.conf.urls import url

from . import views

urlpatterns = [
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/protokoll/(?P<filetype>(html|pdf|txt))/$',
       views.show_protokoll, name="protokoll"),
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/protokoll/templates/$', views.templates,
       name="templates"),
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/protokoll/edit/$', views.edit_protokoll,
       name="editprotokoll"),
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/protokoll/pad/$', views.pad,
       name="pad"),
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/protokoll/publish/$', views.publish_protokoll,
       name="publishprotokoll"),
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/protokoll/publish/success/$',
       views.publish_success, name="successpublish"),
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/protokoll/delete/$', views.delete_protokoll,
       name="delprotokoll"),
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/protokoll/success/$',
       views.success_protokoll, name="successprotokoll"),
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/protokoll/send/$', views.send_protokoll,
       name="sendprotokoll"),
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/protokoll/attachments/$', views.attachments,
       name="attachments"),
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/protokoll/attachments/sort/$',
       views.sort_attachments, name="sortattachments"),
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/protokoll/attachments/(?P<attachment_pk>[0-9]+)/$',
       views.show_attachment, name="showattachment_protokoll"),
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/protokoll/attachments/(?P<attachment_pk>[0-9]+)/edit/$',
       views.edit_attachment, name="editattachment"),
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/protokoll/attachments/(?P<attachment_pk>[0-9]+)/delete/$',
       views.delete_attachment, name="deleteattachment"),
]
