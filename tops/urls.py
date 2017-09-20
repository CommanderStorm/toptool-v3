from django.conf.urls import url

from toptool_common.views import next_view
from . import views

urlpatterns = [
    url(r'^(?P<meeting_pk>[0-9a-f\-]+)/tops/$', views.tops,
        name="edittops"),
    url(r'^(?P<meeting_pk>[0-9a-f\-]+)/tops/sort/$', views.sort_tops,
        name="sorttops"),
    url(r'^nonext/$', views.nonext, name="nonext"),
    url(r'^next/listtops/$', next_view("listtops"), name="nextlisttops"),
    url(r'^(?P<meeting_pk>[0-9a-f\-]+)/listtops/$', views.list,
        name="listtops"),
    url(r'^next/addtop/$', next_view("addtop"), name="nextaddtop"),
    url(r'^(?P<meeting_pk>[0-9a-f\-]+)/addtop/$', views.add, name="addtop"),
    url(r'^(?P<meeting_pk>[0-9a-f\-]+)/edittop/(?P<top_pk>[0-9a-f\-]+)/$',
        views.edit, name="edittop"),
    url(r'^(?P<meeting_pk>[0-9a-f\-]+)/deltop/(?P<top_pk>[0-9a-f\-]+)/$',
        views.delete, name="deltop"),
    url(r'^(?P<meeting_pk>[0-9a-f\-]+)/topattachment/(?P<top_pk>[0-9a-f\-]+)/$',
        views.show_attachment, name="showattachment"),
    url(r'^stdtops/$', views.stdtops, name="liststdtops"),
    url(r'^stdtops/sort/$', views.sort_stdtops, name="sortstdtops"),
    url(r'^addstdtop/$', views.add_std, name="addstdtop"),
    url(r'^editstdtop/(?P<top_pk>[0-9a-f\-]+)/$',
        views.edit_std, name="editstdtop"),
    url(r'^delstdtop/(?P<top_pk>[0-9a-f\-]+)/$',
        views.delete_std, name="delstdtop"),
]
