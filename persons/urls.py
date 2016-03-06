from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^listatt/(?P<meeting_pk>[0-9]+)/$', views.add_attendees,
        name="addattendees"),
    url(r'^editatt/(?P<attendee_pk>[0-9]+)/$', views.edit_attendee,
        name="editattendee"),
    url(r'^delatt/(?P<attendee_pk>[0-9]+)/$', views.delete_attendee,
        name="delattendee"),
    url(r'^functions/(?P<mt_pk>[0-9]+)/$', views.functions, name="functions"),
    url(r'^delfun/(?P<function_pk>[0-9]+)/$', views.delete_function,
        name="delfunction"),
    url(r'^add/(?P<meeting_pk>[0-9]+)/$', views.add_person, name="addperson"),
    url(r'^dels/(?P<mt_pk>[0-9]+)/$', views.delete_persons, name="delpersons"),
    url(r'^del/(?P<person_pk>[0-9]+)/$', views.delete_person,
        name="delperson"),
]
