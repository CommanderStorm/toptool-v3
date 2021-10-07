from django.urls import path

from . import views
from .feeds import MeetingFeed

urlpatterns = [
    path('overview/', views.index, name="ownmts"),
    path('all/', views.index_all, name="allmts"),
    path('all/admins/', views.admins, name="admins"),
    path('add/', views.add, name="addmt"),
    path('<str:mt_pk>/', views.view, name="viewmt"),
    path('<str:mt_pk>/archive/<int:year>/', views.view_archive, name="viewarchive"),
    path('<str:mt_pk>/search/', views.search, name="searchmt"),
    path('<str:mt_pk>/search/archive/<int:year>/', views.search_archive, name="searcharchive"),
    path('<str:mt_pk>/edit/', views.edit_meetingtype, name="editmt"),
    path('<str:mt_pk>/del/', views.delete, name="delmt"),
    path('<str:mt_pk>/upcoming/', views.upcoming, name="upcoming"),
    path('<str:mt_pk>/ical/<uuid:ical_key>/', MeetingFeed(), name="ical"),
]
