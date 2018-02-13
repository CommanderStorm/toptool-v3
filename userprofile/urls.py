from django.conf.urls import url

from . import views
from .feeds import PersonalMeetingFeed

urlpatterns = [
    url(r'^$', views.edit, name="editprofile"),
    url(r'^sortmts/$', views.sort_meetingtypes, name="sortmeetingtypes"),
    url(r'^ical/(?P<ical_key>[0-9a-f\-]+)/$', PersonalMeetingFeed(), name="personalical"),
]
