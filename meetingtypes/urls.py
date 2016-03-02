from django.conf.urls import url

from . import views

urlpatterns = [
   url(r'^$', views.index, name="ownmts"),
   url(r'^all/$', views.index_all, name="allmts"),
   url(r'^add$', views.add, name="addmt"),
   url(r'^(?P<mt_pk>[0-9]+)$', views.view, name="viewmt"),
   url(r'^(?P<mt_pk>[0-9]+)/edit$', views.edit, name="editmt"),
   url(r'^(?P<mt_pk>[0-9]+)/del$', views.delete, name="delmt"),
   url(r'^(?P<mt_pk>[0-9]+)/add$', views.add_meeting, name="addmeeting"),
]

