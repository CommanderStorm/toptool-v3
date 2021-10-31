from django.urls import path

from toptool.views import next_view

from . import views

urlpatterns = [
    path("<uuid:meeting_pk>/tops/", views.edit_tops, name="edittops"),
    path("<uuid:meeting_pk>/tops/sort/", views.sort_tops, name="sorttops"),
    path("nonext/", views.nonext, name="nonext"),
    path("next/listtops/", next_view("listtops"), name="nextlisttops"),
    path("<uuid:meeting_pk>/listtops/", views.list_tops, name="listtops"),
    path("next/addtop/", next_view("addtop"), name="nextaddtop"),
    path("<uuid:meeting_pk>/addtop/", views.add_top, name="addtop"),
    path("<uuid:meeting_pk>/edittop/<uuid:top_pk>/", views.edit_top, name="edittop"),
    path("<uuid:meeting_pk>/deltop/<uuid:top_pk>/", views.delete_top, name="deltop"),
    path(
        "<uuid:meeting_pk>/topattachment/<uuid:top_pk>/",
        views.show_attachment,
        name="showattachment",
    ),
    path("stdtops/", views.stdtops, name="liststdtops"),
    path("stdtops/sort/", views.sort_stdtops, name="sortstdtops"),
    path("addstdtop/", views.add_std, name="addstdtop"),
    path("editstdtop/<uuid:top_pk>/", views.edit_std, name="editstdtop"),
    path("delstdtop/<uuid:top_pk>/", views.delete_std, name="delstdtop"),
]
