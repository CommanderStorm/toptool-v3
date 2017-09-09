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
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/delprotokoll$', views.delete_protokoll,
       name="delprotokoll"),
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/protokollsuccess$',
       views.success_protokoll, name="successprotokoll"),
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/sendprotokoll$', views.send_protokoll,
       name="sendprotokoll"),
]
