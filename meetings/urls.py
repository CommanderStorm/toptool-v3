from django.conf.urls import url

from toptool.views import next_view
from . import views

urlpatterns = [
   url(r'^add/$', views.add, name="addmeeting"),
   url(r'^addseries/$', views.add_series, name="addmeetingseries"),
   url(r'^next/$', next_view("viewmeeting"), name="viewnextmeeting"),
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/$', views.view, name="viewmeeting"),
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/edit/$', views.edit, name="editmeeting"),
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/del/$', views.delete, name="delmeeting"),
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/sendtops/$', views.send_tops,
       name="sendtops"),
   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/sendinvitation/$', views.send_invitation,
       name="sendinvitation"),
]
