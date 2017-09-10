from django.conf.urls import url

from . import views
from .feeds import MeetingFeed

urlpatterns = [
   url(r'^overview/$', views.index, name="ownmts"),
   url(r'^all/$', views.index_all, name="allmts"),
   url(r'^add/$', views.add, name="addmt"),
   url(r'^(?P<mt_pk>[a-z]+)/$', views.view, name="viewmt"),
   url(r'^(?P<mt_pk>[a-z]+)/archive/(?P<year>\d{4})/$', views.view_archive,
       name="viewarchive"),
   url(r'^(?P<mt_pk>[a-z]+)/edit/$', views.edit, name="editmt"),
   url(r'^(?P<mt_pk>[a-z]+)/del/$', views.delete, name="delmt"),
   url(r'^(?P<mt_pk>[a-z]+)/upcoming/$', views.upcoming, name="upcoming"),
   url(r'^(?P<mt_pk>[a-z]+)/ical/$', MeetingFeed(), name="ical"),
]
