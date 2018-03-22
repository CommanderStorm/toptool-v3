from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<meeting_pk>[0-9a-f\-]+)/addatt/$', views.add_attendees,
        name="addattendees"),
    url(r'^(?P<meeting_pk>[0-9a-f\-]+)/editatt/(?P<attendee_pk>[0-9]+)/$',
        views.edit_attendee, name="editattendee"),
    url(r'^(?P<meeting_pk>[0-9a-f\-]+)/delatt/(?P<attendee_pk>[0-9]+)/$',
        views.delete_attendee, name="delattendee"),
    url(r'^functions/$', views.functions, name="functions"),
    url(r'^functions/sort/$', views.sort_functions, name="sortfunctions"),
    url(r'^functions/(?P<function_pk>[0-9]+)/edit/$', views.edit_function,
        name="editfunction"),
    url(r'^functions/(?P<function_pk>[0-9]+)/delete/$', views.delete_function,
        name="delfunction"),
    url(r'^(?P<meeting_pk>[0-9a-f\-]+)/addperson/$', views.add_person,
        name="addperson"),
    url(r'^persons/$', views.persons, name="persons"),
    url(r'^persons/add/$', views.add_plain_person,
        name="addplainperson"),
    url(r'^persons/(?P<person_pk>[0-9]+)/edit/$', views.edit_person,
        name="editperson"),
    url(r'^persons/(?P<person_pk>[0-9]+)/delete/$', views.delete_person,
        name="delperson"),
]
