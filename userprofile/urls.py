from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^edit/$', views.edit, name="editprofile"),
    url(r'^edit/sortmts/$', views.sort_meetingtypes, name="sortmeetingtypes"),
]
