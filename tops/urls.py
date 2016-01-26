from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<meeting_pk>[0-9]+)/$', views.view, name="viewtops"),
    url(r'^add/(?P<meeting_pk>[0-9]+)/$', views.add, name="addtop"),
    url(r'^del/(?P<meeting_pk>[0-9]+)/$', views.delete, name="deltop"),
]

