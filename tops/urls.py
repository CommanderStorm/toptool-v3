from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<meeting_pk>[0-9]+)/$', views.view, name="viewtops"),
    url(r'^(?P<meeting_pk>[0-9]+)/add$', views.add, name="addtop"),
    url(r'^(?P<meeting_pk>[0-9]+)/del$', views.delete, name="deltop"),
]

