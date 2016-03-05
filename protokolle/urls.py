from django.conf.urls import url

from . import views

urlpatterns = [
   url(r'^(?P<meeting_pk>[0-9]+)/(?P<filetype>(html|pdf|txt))/$',
       views.show_protokoll, name="protokoll"),
   url(r'^(?P<meeting_pk>[0-9]+)/template/$', views.template, name="template"),
   url(r'^edit/(?P<meeting_pk>[0-9]+)/$', views.edit_protokoll,
       name="editprotokoll"),
   url(r'^del/(?P<meeting_pk>[0-9]+)/$', views.delete_protokoll,
       name="delprotokoll"),
   url(r'^success/(?P<meeting_pk>[0-9]+)/$', views.success_protokoll,
       name="successprotokoll"),
]

