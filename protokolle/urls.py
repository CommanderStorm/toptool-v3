from django.conf.urls import url

from . import views

urlpatterns = [
   url(r'^(?P<meeting_pk>[0-9]+)/(?P<filetype>(html|pdf|txt))/$',
       views.show_protokoll, name="protokoll"),
   url(r'^(?P<meeting_pk>[0-9]+)/template/$', views.template, name="template"),
   url(r'^(?P<meeting_pk>[0-9]+)/templatefilled/$', views.template_filled,
       name="templatefilled"),
   url(r'^edit/(?P<meeting_pk>[0-9]+)/$', views.edit_protokoll,
       name="editprotokoll"),
   url(r'^del/(?P<meeting_pk>[0-9]+)/$', views.delete_protokoll,
       name="delprotokoll"),
   url(r'^success/(?P<meeting_pk>[0-9]+)/$', views.success_protokoll,
       name="successprotokoll"),
   url(r'^send/(?P<meeting_pk>[0-9]+)/$', views.send_protokoll,
       name="sendprotokoll"),
]
