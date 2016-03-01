from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<meeting_pk>[0-9]+)/$', views.list, name="listtops"),
    url(r'^(?P<meeting_pk>[0-9]+)/add$', views.add, name="addtop"),
    url(r'^(?P<meeting_pk>[0-9]+)/(?P<topid>[0-9]+)/edit$', views.edit,
        name="edittop"),
    url(r'^(?P<meeting_pk>[0-9]+)/(?P<topid>[0-9]+)/del$', views.delete,
        name="deltop"),
    url(r'^(?P<meeting_pk>[0-9]+)/del$', views.delete, name="deltop"),
]

