import urllib.parse
from collections import OrderedDict
from typing import List

from django import forms
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Permission, Group, User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.clickjacking import xframe_options_exempt

from protokolle.models import Protokoll
from toptool.shortcuts import render
from .forms import MTForm, MTAddForm
from .models import MeetingType


# list all meetingtypes the user is a member of
# (allowed only by logged users)
@login_required
def index(request: WSGIRequest) -> HttpResponse:
    meetingtypes = MeetingType.objects.order_by('name')
    mts_with_perm = []
    for meetingtype in meetingtypes:
        if request.user.has_perm(meetingtype.permission()):
            mts_with_perm.append(meetingtype)

    if len(mts_with_perm) == 1:
        return redirect('viewmt', mts_with_perm[0].pk)

    mt_preferences = {
        mtp.meetingtype.pk: mtp.sortid for mtp in
        request.user.meetingtypepreference_set.all()
    }
    if mt_preferences:
        max_sortid = max(mt_preferences.values()) + 1
    else:
        max_sortid = 1
    mts_with_perm.sort(
        key=lambda mt: (mt_preferences.get(mt.pk, max_sortid), mt.name)
    )
    context = {
        'mts_with_perm': mts_with_perm,
    }
    return render(request, 'meetingtypes/index.html', context)


# admin interface: view all meetingtypes (allowed only by staff)
@login_required
@user_passes_test(lambda u: u.is_staff)
def index_all(request: WSGIRequest) -> HttpResponse:
    all_meetingtypes = MeetingType.objects.order_by('name')
    context = {
        'all_meetingtypes': all_meetingtypes,
    }
    return render(request, 'meetingtypes/index_all.html', context)


# list all email addresses of admins and meetingtype admins
# (allowed only by staff)
@login_required
@user_passes_test(lambda u: u.is_staff)
def admins(request: WSGIRequest) -> HttpResponse:
    meetingtypes = MeetingType.objects.all()
    admin_users = list(User.objects.filter(is_staff=True))
    for meetingtype in meetingtypes:
        new_users = User.objects.filter(
            Q(user_permissions=meetingtype.get_admin_permission()) |
            Q(groups__permissions=meetingtype.get_admin_permission())
        ).distinct()
        for user in new_users:
            if user not in admin_users:
                admin_users.append(user)
    context = {
        'admins': admin_users,
    }
    return render(request, 'meetingtypes/admins.html', context)


def search(request: WSGIRequest, mt_pk: str) -> HttpResponse:
    return view_all(request, mt_pk, search=True)


def search_archive(request: WSGIRequest, mt_pk: str, year: int) -> HttpResponse:
    return view_archive_all(request, mt_pk, year, search=True)


def view(request: WSGIRequest, mt_pk: str) -> HttpResponse:
    return view_all(request, mt_pk, search=False)


def view_archive(request: WSGIRequest, mt_pk: str, year: int) -> HttpResponse:
    return view_archive_all(request, mt_pk, year, search=False)


def _get_param(request: WSGIRequest, name: str, default: str = "") -> str:
    value: str = request.POST.get(name, default=None)
    if value is None:
        value = request.GET.get(name, default=default)
    return value


def _search_meeting(request: WSGIRequest, meeting, search_query) -> List[str]:
    location = []
    top_set = list(meeting.top_set.order_by('topid'))
    if top_set is not None:
        for top in top_set:
            if (top.title is not None and search_query in top.title.lower()) or (
                    top.description is not None and search_query in top.description.lower()):
                location.append("Tagesordnung")
                break
    try:
        protokoll = meeting.protokoll
    except Protokoll.DoesNotExist:
        protokoll = None
    if protokoll is not None and protokoll.filepath is not None:
        if (not protokoll.published and not
        (request.user.has_perm(meeting.meetingtype.admin_permission()) or
         request.user == meeting.sitzungsleitung or
         request.user in meeting.minute_takers.all())):
            return location
        if not protokoll.approved and not request.user.is_authenticated:
            return location
        with open(protokoll.filepath + ".txt", "r") as f:
            content = f.read()
            if content is not None and search_query in content.lower():
                location.append("Protokoll")
    return location


def _search_meetinglist(request: WSGIRequest, meetings, search_query) -> OrderedDict:
    meeting_location = OrderedDict()
    for meeting in meetings:
        location = []
        title = meeting.title
        if title is None or title == '':
            title = meeting.meetingtype.defaultmeetingtitle
        if title is not None and search_query in title.lower():
            location.append("Titel")
        location.extend(_search_meeting(request, meeting, search_query))
        if len(location) > 0:
            meeting_location[meeting] = location
    return meeting_location


# view single meetingtype (allowed only by users with permission for that
# meetingtype or allowed for public if public-bit set)
def view_all(request: WSGIRequest, mt_pk: str, search: bool) -> HttpResponse:
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    if not meetingtype.public:  # public access disabled
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        if not request.user.has_perm(meetingtype.permission()):
            raise PermissionDenied
    year = timezone.now().year
    past_meetings = meetingtype.past_meetings_by_year(year).order_by('-time')
    upcoming_meetings = meetingtype.upcoming_meetings.order_by('time')
    years = list(filter(lambda y: y <= year, meetingtype.years))
    if year not in years:
        years.append(year)
    search_query = _get_param(request, "query").lower()
    if search:
        if search_query is None or search_query == '':
            return redirect('viewmt', mt_pk)
        past_meetings = _search_meetinglist(request, past_meetings, search_query)
        upcoming_meetings = _search_meetinglist(request, upcoming_meetings, search_query)
    else:
        past_meetings_tmp = OrderedDict()
        for meeting in past_meetings:
            past_meetings_tmp[meeting] = ''
        past_meetings = past_meetings_tmp
        upcoming_meetings_tmp = OrderedDict()
        for meeting in upcoming_meetings:
            upcoming_meetings_tmp[meeting] = ''
        upcoming_meetings = upcoming_meetings_tmp

    index = years.index(year)
    if index > 0:
        prev_year = years[index - 1]
    else:
        prev_year = None

    try:
        next_year = years[index + 1]
    except IndexError:
        next_year = None

    ical_url = None
    if meetingtype.ical_key:
        ical_url = request.build_absolute_uri(
            reverse('ical', args=[meetingtype.pk, meetingtype.ical_key]))

    context = {'meetingtype': meetingtype,
               'years': years,
               'current': year,
               'prev': prev_year,
               'next': next_year,
               'ical_url': ical_url,
               'past_meetings': past_meetings,
               'upcoming_meetings': upcoming_meetings,
               'search_query': search_query,
               'search': search}
    return render(request, 'meetingtypes/view.html', context)


# view meeting archive for given year (allowed only by users with permission
# for that meetingtype or allowed for public if public-bit set)
def view_archive_all(request: WSGIRequest, mt_pk: str, year: int, search: bool) -> HttpResponse:
    year = int(year)
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    if not meetingtype.public:  # public access disabled
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        if not request.user.has_perm(meetingtype.permission()):
            raise PermissionDenied

    search_query = _get_param(request, "query")

    if year >= timezone.now().year:
        if search:
            response = redirect('searchmt', mt_pk)
            response['location'] += '?' + urllib.parse.urlencode({'query': search_query})
            return response
        return redirect('viewmt', mt_pk)

    meetings = meetingtype.past_meetings_by_year(year).order_by('time')
    years = list(filter(lambda y: y <= timezone.now().year, meetingtype.years))

    if search:
        if search_query is None or search_query == '':
            return redirect('viewarchive', mt_pk, year)
        meetings = _search_meetinglist(request, meetings, search_query)
    else:
        meetings_tmp = OrderedDict()
        for meeting in meetings:
            meetings_tmp[meeting] = ''
        meetings = meetings_tmp

    if year not in years:
        return redirect('viewmt', mt_pk)

    year_now = timezone.now().year
    if year_now not in years:
        years.append(timezone.now().year)

    index = years.index(year)
    if index > 0:
        prev_year = years[index - 1]
    else:
        prev_year = None

    try:
        next_year = years[index + 1]
    except IndexError:
        next_year = None

    context = {'meetingtype': meetingtype,
               'meetings': meetings,
               'prev': prev_year,
               'next': next_year,
               'years': years,
               'current': year,
               'search_query': search_query,
               'search': search,
               'year_now': year_now}
    return render(request, 'meetingtypes/view_archive.html', context)


# create meetingtype (allowed only by staff)
@login_required
@user_passes_test(lambda u: u.is_staff)
def add(request: WSGIRequest) -> HttpResponse:
    form = MTAddForm(request.POST or None)
    if form.is_valid():
        meetingtype = form.save()
        content_type = ContentType.objects.get_for_model(MeetingType)

        groups = form.cleaned_data['groups']
        users = form.cleaned_data['users']
        admin_groups = form.cleaned_data['admin_groups']
        admin_users = form.cleaned_data['admin_users']

        permission = Permission.objects.create(
            codename=meetingtype.id, name="permission for " + meetingtype.name,
            content_type=content_type)

        admin_permission = Permission.objects.create(
            codename=meetingtype.id + MeetingType.ADMIN,
            name="admin_permission for " + meetingtype.name,
            content_type=content_type)

        for g in groups:
            g.permissions.add(permission)
        for u in users:
            u.user_permissions.add(permission)
        for g in admin_groups:
            g.permissions.add(permission)
            g.permissions.add(admin_permission)
        for u in admin_users:
            u.user_permissions.add(permission)
            u.user_permissions.add(admin_permission)

        return redirect('allmts')

    context = {
        'add': True,
        'form': form,
    }
    return render(request, 'meetingtypes/edit.html', context)


# edit meetingtype (allowed only by meetingtype-admin or staff)
@login_required
def edit_meetingtype(request: WSGIRequest, mt_pk: str) -> HttpResponse:
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    if not request.user.has_perm(meetingtype.admin_permission()) and not \
            request.user.is_staff:
        raise PermissionDenied

    groups = Group.objects.filter(
        permissions=meetingtype.get_permission()).order_by('name')
    users = User.objects.filter(
        user_permissions=meetingtype.get_permission()
    ).order_by('first_name', 'last_name', 'username')
    admin_groups = Group.objects.filter(
        permissions=meetingtype.get_admin_permission()).order_by('name')
    admin_users = User.objects.filter(
        user_permissions=meetingtype.get_admin_permission()
    ).order_by('first_name', 'last_name', 'username')

    initial_values = {
        'groups': groups,
        'users': users,
        'admin_groups': admin_groups,
        'admin_users': admin_users,
    }

    form = MTForm(request.POST or None, instance=meetingtype,
                  initial=initial_values)
    if form.is_valid():
        meetingtype = form.save()
        content_type = ContentType.objects.get_for_model(MeetingType)

        groups_ = form.cleaned_data['groups']
        users_ = form.cleaned_data['users']
        admin_groups_ = form.cleaned_data['admin_groups']
        admin_users_ = form.cleaned_data['admin_users']

        permission = meetingtype.get_permission()
        admin_permission = meetingtype.get_admin_permission()

        # first remove all revoked permissions
        for g in groups:
            if g not in groups_:
                g.permissions.remove(permission)
        for u in users:
            if u not in users_:
                u.user_permissions.remove(permission)
        for g in admin_groups:
            if g not in admin_groups_:
                g.permissions.remove(permission)
                g.permissions.remove(admin_permission)
        for u in admin_users:
            if u not in admin_users_:
                u.user_permissions.remove(permission)
                u.user_permissions.remove(admin_permission)

        # then set all new permissions
        for g in groups_:
            if g not in groups:
                g.permissions.add(permission)
        for u in users_:
            if u not in users:
                u.user_permissions.add(permission)
        for g in admin_groups_:
            if g not in admin_groups:
                g.permissions.add(permission)
                g.permissions.add(admin_permission)
        for u in admin_users_:
            if u not in admin_users:
                u.user_permissions.add(permission)
                u.user_permissions.add(admin_permission)

        return redirect('viewmt', meetingtype.id)

    context = {'meetingtype': meetingtype,
               'add': False,
               'form': form}
    return render(request, 'meetingtypes/edit.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def delete(request: WSGIRequest, mt_pk: str) -> HttpResponse:
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    form = forms.Form(request.POST or None)
    if form.is_valid():
        meetingtype.delete()

        return redirect('allmts')

    context = {'meetingtype': meetingtype,
               'form': form}
    return render(request, 'meetingtypes/del.html', context)


# show upcoming meetings for one meetingtype (allowed only by users with
# permission for that meetingtype or allowed for public if public-bit set)
@xframe_options_exempt
def upcoming(request: WSGIRequest, mt_pk: str) -> HttpResponse:
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    if not meetingtype.public:  # public access disabled
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        if not request.user.has_perm(meetingtype.permission()):
            raise PermissionDenied

    upcoming_meetings = meetingtype.upcoming_meetings.order_by('time')

    context = {'meetingtype': meetingtype,
               'upcoming_meetings': upcoming_meetings}
    return render(request, 'meetingtypes/upcoming.html', context)
