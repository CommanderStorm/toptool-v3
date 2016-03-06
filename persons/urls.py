from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<meeting_pk>[0-9a-f\-]+)/addatt/$', views.add_attendees,
        name="addattendees"),
    url(r'^(?P<meeting_pk>[0-9a-f\-]+)/editatt/(?P<attendee_pk>[0-9a-f\-]+)/$',
        views.edit_attendee, name="editattendee"),
    url(r'^(?P<meeting_pk>[0-9a-f\-]+)/delatt/(?P<attendee_pk>[0-9a-f\-]+)/$',
        views.delete_attendee, name="delattendee"),
    url(r'^functions/$', views.functions, name="functions"),
    url(r'^delfun/(?P<function_pk>[0-9a-f\-]+)/$', views.delete_function,
        name="delfunction"),
    url(r'^(?P<meeting_pk>[0-9a-f\-]+)/addperson$', views.add_person,
        name="addperson"),
    url(r'^delpersons$', views.delete_persons, name="delpersons"),
    url(r'^delperson/(?P<person_pk>[0-9a-f\-]+)/$', views.delete_person,
        name="delperson"),
]
