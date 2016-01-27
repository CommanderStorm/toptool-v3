from django.conf.urls import url

from . import views

urlpatterns = [
   url(r'^$', views.index, name="index"),
   url(r'^(?P<meeting_pk>[0-9]+)/$', views.view, name="viewmeeting"),
   url(r'^(?P<meeting_pk>[0-9]+)/sendtops$', views.send_tops, name="sendtops"),
]

