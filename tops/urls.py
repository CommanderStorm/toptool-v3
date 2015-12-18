from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<meeting_pk>[0-9]+)/$', views.view, name="view"),
    url(r'^add/(?P<meeting_pk>[0-9]+)/$', views.add, name="add"),
    url(r'^del/(?P<meeting_pk>[0-9]+)/$', views.delete, name="del"),
]

