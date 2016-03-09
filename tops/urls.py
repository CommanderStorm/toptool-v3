from django.conf.urls import url

from toptool_common.views import next_view
from . import views

urlpatterns = [
    url(r'^next/listtops/$', next_view("listtops"), name="nextlisttops"),
    url(r'^(?P<meeting_pk>[0-9a-f\-]+)/listtops/$', views.list,
        name="listtops"),
    url(r'^next/addtop/$', next_view("addtop"), name="nextaddtop"),
    url(r'^(?P<meeting_pk>[0-9a-f\-]+)/addtop/$', views.add, name="addtop"),
    url(r'^(?P<meeting_pk>[0-9a-f\-]+)/edittop/(?P<top_pk>[0-9a-f\-]+)/$',
        views.edit, name="edittop"),
    url(r'^(?P<meeting_pk>[0-9a-f\-]+)/deltop/(?P<top_pk>[0-9a-f\-]+)/$',
        views.delete, name="deltop"),
    url(r'^addstdtop/$', views.add_std, name="addstdtop"),
    url(r'^editstdtop/(?P<top_pk>[0-9a-f\-]+)/$',
        views.edit_std, name="editstdtop"),
    url(r'^delstdtop/(?P<top_pk>[0-9a-f\-]+)/$',
        views.delete_std, name="delstdtop"),
]
