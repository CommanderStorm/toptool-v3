from django.urls import path

from toptool.views import next_view

from . import views

# app_name = "tops"
urlpatterns = [
    path("<str:mt_pk>/<uuid:meeting_pk>/tops/", views.edit_tops, name="edittops"),
    path("<str:mt_pk>/<uuid:meeting_pk>/tops/sort/", views.sort_tops, name="sorttops"),
    path("<str:mt_pk>/nonext/", views.nonext, name="nonext"),
    path("<str:mt_pk>/next/listtops/", next_view("listtops"), name="nextlisttops"),
    path("<str:mt_pk>/<uuid:meeting_pk>/listtops/", views.list_tops, name="listtops"),
    path("<str:mt_pk>/next/addtop/", next_view("addtop"), name="nextaddtop"),
    path("<str:mt_pk>/<uuid:meeting_pk>/addtop/", views.add_top, name="addtop"),
    path("<str:mt_pk>/<uuid:meeting_pk>/edittop/<uuid:top_pk>/", views.edit_top, name="edittop"),
    path("<str:mt_pk>/<uuid:meeting_pk>/deltop/<uuid:top_pk>/", views.delete_top, name="deltop"),
    path("<str:mt_pk>/<uuid:meeting_pk>/topattachment/<uuid:top_pk>/",views.show_attachment,name="showattachment",),
    path("<str:mt_pk>/stdtops/", views.stdtops, name="liststdtops"),
    path("<str:mt_pk>/stdtops/sort/", views.sort_stdtops, name="sortstdtops"),
    path("<str:mt_pk>/addstdtop/", views.add_std, name="addstdtop"),
    path("<str:mt_pk>/editstdtop/<uuid:top_pk>/", views.edit_std, name="editstdtop"),
    path("<str:mt_pk>/delstdtop/<uuid:top_pk>/", views.delete_std, name="delstdtop"),
]
