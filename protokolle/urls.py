from django.conf.urls import url

from . import views

urlpatterns = [
   url(r'^(?P<meeting_pk>[0-9]+)/(?P<filetype>(html|pdf|txt))$', views.protokoll,
       name="protokoll"),
   url(r'^(?P<meeting_pk>[0-9]+)/template$', views.template, name="template"),
]

