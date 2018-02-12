from django.conf.urls import url

from . import views
from .feeds import PersonalMeetingFeed

urlpatterns = [
    url(r'^edit/$', views.edit, name="editprofile"),
    url(r'^edit/sortmts/$', views.sort_meetingtypes, name="sortmeetingtypes"),
    url(r'^ical/(?P<ical_key>[0-9a-f\-]+)/$', PersonalMeetingFeed(), name="personalical"),
]
