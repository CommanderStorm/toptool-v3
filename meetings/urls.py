from django.conf.urls import url

from . import views

urlpatterns = [
   url(r'^(?P<meeting_pk>[0-9]+)/$', views.view, name="viewmeeting"),
   url(r'^(?P<meeting_pk>[0-9]+)/edit/$', views.edit, name="editmeeting"),
   url(r'^(?P<meeting_pk>[0-9]+)/del/$', views.delete, name="delmeeting"),
   url(r'^(?P<meeting_pk>[0-9]+)/sendtops/$', views.send_tops, name="sendtops"),
   url(r'^(?P<meeting_pk>[0-9]+)/sendinvitation/$', views.send_invitation,
       name="sendinvitation"),
]

