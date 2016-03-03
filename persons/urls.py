from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^list/(?P<meeting_pk>[0-9]+)/$', views.add_attendees, name="addattendees"),
    url(r'^edit/(?P<attendee_pk>[0-9]+)/$', views.edit_attendee, name="editattendee"),
    url(r'^del/(?P<attendee_pk>[0-9]+)/$', views.delete_attendee, name="delattendee"),
    url(r'^add/(?P<meeting_pk>[0-9]+)/$', views.add_person, name="addperson"),
]

