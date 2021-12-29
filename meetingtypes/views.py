import urllib.parse
from collections import OrderedDict
from typing import List, Optional

from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.views import redirect_to_login
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q, QuerySet
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.clickjacking import xframe_options_exempt

from meetings.models import Meeting
from protokolle.models import Protokoll
from toptool.utils.permission import auth_login_required
from toptool.utils.shortcuts import get_permitted_mts_sorted, render
from toptool.utils.typing import AuthWSGIRequest

from .forms import MTAddForm, MTForm
from .models import MeetingType


# list all meetingtypes the user is a member of
# (allowed only by logged users)
def index(request: WSGIRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        # required, because we need at least one view for unauthenticated users.
        error_message = _("Bitte logge dich ein, um alles zu sehen")
        all_messages_content = [msg.message for msg in list(messages.get_messages(request))]
        if error_message not in all_messages_content:
            messages.warning(request, error_message)
        return render(request, "base.html", {})

    mts_with_perm = get_permitted_mts_sorted(request.user)

    if len(mts_with_perm) == 1:
        return redirect("meetingtypes:view_meetingtype", mts_with_perm[0].pk)

    context = {
        "mts_with_perm": mts_with_perm,
    }
    return render(request, "meetingtypes/index.html", context)


# admin interface: view all meetingtypes (allowed only by staff)
@auth_login_required()
@user_passes_test(lambda u: u.is_staff)
def list_meetingtypes(request: AuthWSGIRequest) -> HttpResponse:
    all_meetingtypes = MeetingType.objects.order_by("name")
    context = {
        "all_meetingtypes": all_meetingtypes,
    }
    return render(request, "meetingtypes/index_all.html", context)


# list all email addresses of admins and meetingtype admins
# (allowed only by staff)
@auth_login_required()
@user_passes_test(lambda u: u.is_staff)
def list_admins(request: AuthWSGIRequest) -> HttpResponse:
    meetingtypes = MeetingType.objects.all()
    admin_users = list(get_user_model().objects.filter(is_staff=True))
    for meetingtype in meetingtypes:
        new_users = (
            get_user_model()
            .objects.filter(
                Q(user_permissions=meetingtype.get_admin_permission())
                | Q(groups__permissions=meetingtype.get_admin_permission()),
            )
            .distinct()
        )
        for user in new_users:
            if user not in admin_users:
                admin_users.append(user)
    context = {
        "admins": admin_users,
    }
    return render(request, "meetingtypes/admins.html", context)


def search(request: WSGIRequest, mt_pk: str) -> HttpResponse:
    return view_all(request, mt_pk, search_mt=True)


def search_archive(request: WSGIRequest, mt_pk: str, year: int) -> HttpResponse:
    return view_archive_all(request, mt_pk, year, search_archive_flag=True)


def view_archive(request: WSGIRequest, mt_pk: str, year: int) -> HttpResponse:
    return view_archive_all(request, mt_pk, year, search_archive_flag=False)


def view_meetingtype(request: WSGIRequest, mt_pk: str) -> HttpResponse:
    return view_all(request, mt_pk, search_mt=False)


def _get_param(request: WSGIRequest, name: str, default: str = "") -> str:
    value: Optional[str] = request.POST.get(name, default=None)
    if value:
        return value
    return request.GET.get(name, default=default)


def _search_meeting(request: WSGIRequest, meeting: Meeting, search_query: str) -> List[str]:
    location = []
    top_set = list(meeting.top_set.order_by("topid"))
    if top_set is not None:
        for top in top_set:
            if (top.title is not None and search_query in top.title.lower()) or (
                top.description is not None and search_query in top.description.lower()
            ):
                location.append("Tagesordnung")
                break
    try:
        protokoll: Optional[Protokoll] = meeting.protokoll
    except Protokoll.DoesNotExist:
        protokoll = None
    if protokoll is not None and protokoll.filepath is not None:
        if not protokoll.published and not (
            request.user.has_perm(meeting.meetingtype.admin_permission())
            or request.user == meeting.sitzungsleitung
            or request.user in meeting.minute_takers.all()
        ):
            return location
        if not protokoll.approved and not request.user.is_authenticated:
            return location
        with open(protokoll.filepath + ".txt", "r") as file:
            content = file.read()
            if content is not None and search_query in content.lower():
                location.append("Protokoll")
    return location


def _search_meetinglist(
    request: WSGIRequest,
    meetings: QuerySet[Meeting],
    search_query: str,
) -> OrderedDict[Meeting, List[str]]:
    meeting_location = OrderedDict()
    meeting: Meeting
    for meeting in meetings:
        location: List[str] = []
        title = meeting.title
        if title is None or title == "":
            title = meeting.meetingtype.defaultmeetingtitle
        if title is not None and search_query in title.lower():
            location.append("Titel")
        location.extend(_search_meeting(request, meeting, search_query))
        if len(location) > 0:
            meeting_location[meeting] = location
    return meeting_location


# view single meetingtype (allowed only by users with permission for that
# meetingtype or allowed for public if public-bit set)
def view_all(request: WSGIRequest, mt_pk: str, search_mt: bool) -> HttpResponse:
    meetingtype: MeetingType = get_object_or_404(MeetingType, pk=mt_pk)
    if not meetingtype.public:  # public access disabled
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not request.user.has_perm(meetingtype.permission()):
            raise PermissionDenied
    year = timezone.now().year
    past_meetings_qs: QuerySet[Meeting] = meetingtype.past_meetings_by_year(
        year,
        reverse_order=True,
    )
    upcoming_meetings_qs: QuerySet[Meeting] = meetingtype.upcoming_meetings
    years = list(filter(lambda y: y <= year, meetingtype.years))
    if year not in years:
        years.append(year)
    search_query: str = _get_param(request, "query").lower()
    if search_mt:
        if search_query is None or search_query == "":
            return redirect("meetingtypes:view_meetingtype", mt_pk)
        past_meetings: OrderedDict[Meeting, List[str]] = _search_meetinglist(
            request,
            past_meetings_qs,
            search_query,
        )
        upcoming_meetings_dict: OrderedDict[Meeting, List[str]] = _search_meetinglist(
            request,
            upcoming_meetings_qs,
            search_query,
        )
    else:
        past_meetings = OrderedDict()
        for meeting in past_meetings:
            past_meetings[meeting] = []
        upcoming_meetings_dict = OrderedDict()
        for meeting in upcoming_meetings_qs:
            upcoming_meetings_dict[meeting] = []

    prev_year, next_year = _get_surrounding_years(years, year)

    ical_url = None
    if meetingtype.ical_key:
        ical_url = request.build_absolute_uri(
            reverse("meetingtypes:ical_meeting_feed", args=[meetingtype.pk, meetingtype.ical_key]),
        )

    context = {
        "meetingtype": meetingtype,
        "years": years,
        "current": year,
        "prev": prev_year,
        "next": next_year,
        "ical_url": ical_url,
        "past_meetings": past_meetings,
        "upcoming_meetings": upcoming_meetings_dict,
        "search_query": search_query,
        "search": search_mt,
    }
    return render(request, "meetingtypes/view.html", context)


def _get_surrounding_years(years, year):
    year_index = years.index(year)
    if year_index > 0:
        prev_year: Optional[int] = years[year_index - 1]
    else:
        prev_year = None
    if year_index + 1 < len(years):
        next_year: Optional[int] = years[year_index + 1]
    else:
        next_year = None
    return prev_year, next_year


# view meeting archive for given year (allowed only by users with permission
# for that meetingtype or allowed for public if public-bit set)
def view_archive_all(request: WSGIRequest, mt_pk: str, year: int, search_archive_flag: bool) -> HttpResponse:
    if not 1950 < year < 2050:
        raise Http404("Invalid year. Asserted to be between 1950 and 2050")
    meetingtype: MeetingType = get_object_or_404(MeetingType, pk=mt_pk)
    if not meetingtype.public:  # public access disabled
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not request.user.has_perm(meetingtype.permission()):
            raise PermissionDenied

    search_query = _get_param(request, "query")

    if year >= timezone.now().year:
        if search_archive_flag:
            response = redirect("meetingtypes:search_meetingtype", meetingtype.id)
            response["location"] += "?" + urllib.parse.urlencode(
                {"query": search_query},
            )
            return response
        return redirect("meetingtypes:view_meetingtype", mt_pk)

    meetings_qs: QuerySet[Meeting] = meetingtype.past_meetings_by_year(year)
    years: List[int] = [year for year in meetingtype.years if year <= timezone.now().year]

    if search_archive_flag:
        if search_query is None or search_query == "":
            return redirect("meetingtypes:view_archive", mt_pk, year)
        meetings: OrderedDict[Meeting, List[str]] = _search_meetinglist(
            request,
            meetings_qs,
            search_query,
        )
    else:
        meetings = OrderedDict()
        for meeting in meetings_qs:
            meetings[meeting] = []

    if year not in years:
        return redirect("meetingtypes:view_meetingtype", mt_pk)

    year_now: int = timezone.now().year
    if year_now not in years:
        years.append(year_now)

    prev_year, next_year = _get_surrounding_years(years, year)

    context = {
        "meetingtype": meetingtype,
        "meetings": meetings,
        "prev": prev_year,
        "next": next_year,
        "years": years,
        "current": year,
        "search_query": search_query,
        "search": search_archive_flag,
        "year_now": year_now,
    }
    return render(request, "meetingtypes/view_archive.html", context)


# create meetingtype (allowed only by staff)
@auth_login_required()
@user_passes_test(lambda u: u.is_staff)
def add_meetingtype(request: AuthWSGIRequest) -> HttpResponse:
    form = MTAddForm(request.POST or None)
    if form.is_valid():
        meetingtype = form.save()
        content_type = ContentType.objects.get_for_model(MeetingType)

        groups = form.cleaned_data["groups"]
        users = form.cleaned_data["users"]
        admin_groups = form.cleaned_data["admin_groups"]
        admin_users = form.cleaned_data["admin_users"]

        permission = Permission.objects.create(
            codename=meetingtype.id,
            name="permission for " + meetingtype.name,
            content_type=content_type,
        )

        admin_permission = Permission.objects.create(
            codename=meetingtype.id + MeetingType.ADMIN,
            name="admin_permission for " + meetingtype.name,
            content_type=content_type,
        )

        for group in groups:
            group.permissions.add(permission)
        for user in users:
            user.user_permissions.add(permission)
        for admin_group in admin_groups:
            admin_group.permissions.add(permission)
            admin_group.permissions.add(admin_permission)
        for admin_user in admin_users:
            admin_user.user_permissions.add(permission)
            admin_user.user_permissions.add(admin_permission)

        return redirect("meetingtypes:list_meetingtypes")

    context = {
        "add": True,
        "form": form,
    }
    return render(request, "meetingtypes/edit.html", context)


# edit meetingtype (allowed only by meetingtype-admin or staff)
@auth_login_required()
def edit_meetingtype(request: AuthWSGIRequest, mt_pk: str) -> HttpResponse:
    meetingtype: MeetingType = get_object_or_404(MeetingType, pk=mt_pk)
    if not request.user.has_perm(meetingtype.admin_permission()) and not request.user.is_staff:
        raise PermissionDenied

    groups = Group.objects.filter(
        permissions=meetingtype.get_permission(),
    ).order_by("name")
    users = (
        get_user_model()
        .objects.filter(
            user_permissions=meetingtype.get_permission(),
        )
        .order_by("first_name", "last_name", "username")
    )
    admin_groups = Group.objects.filter(
        permissions=meetingtype.get_admin_permission(),
    ).order_by("name")
    admin_users = (
        get_user_model()
        .objects.filter(
            user_permissions=meetingtype.get_admin_permission(),
        )
        .order_by("first_name", "last_name", "username")
    )

    initial_values = {
        "groups": groups,
        "users": users,
        "admin_groups": admin_groups,
        "admin_users": admin_users,
    }

    form = MTForm(
        request.POST or None,
        instance=meetingtype,
        initial=initial_values,
    )
    if form.is_valid():
        meetingtype = form.save()
        ContentType.objects.get_for_model(
            MeetingType,
        )  # creates ContentType if necessary

        groups_ = form.cleaned_data["groups"]
        users_ = form.cleaned_data["users"]
        admin_groups_ = form.cleaned_data["admin_groups"]
        admin_users_ = form.cleaned_data["admin_users"]

        permission = meetingtype.get_permission()
        admin_permission = meetingtype.get_admin_permission()

        _recalculate_permissions(
            permission,
            admin_permission,
            admin_groups,
            admin_groups_,
            admin_users,
            admin_users_,
            groups,
            groups_,
            users,
            users_,
        )

        return redirect("meetingtypes:view_meetingtype", meetingtype.id)

    context = {
        "meetingtype": meetingtype,
        "add": False,
        "form": form,
    }
    return render(request, "meetingtypes/edit.html", context)


# pylint: disable=too-many-arguments
# pylint: disable=too-many-branches
def _recalculate_permissions(
    permission,
    admin_permission,
    admin_groups,
    admin_groups_,
    admin_users,
    admin_users_,
    groups,
    groups_,
    users,
    users_,
):
    # first remove all revoked permissions
    for group in groups:
        if group not in groups_:
            group.permissions.remove(permission)
    for user in users:
        if user not in users_:
            user.user_permissions.remove(permission)
    for admin_group in admin_groups:
        if admin_group not in admin_groups_:
            admin_group.permissions.remove(permission)
            admin_group.permissions.remove(admin_permission)
    for admin_user in admin_users:
        if admin_user not in admin_users_:
            admin_user.user_permissions.remove(permission)
            admin_user.user_permissions.remove(admin_permission)
    # then set all new permissions
    for group in groups_:
        if group not in groups:
            group.permissions.add(permission)
    for user in users_:
        if user not in users:
            user.user_permissions.add(permission)
    for admin_group in admin_groups_:
        if admin_group not in admin_groups:
            admin_group.permissions.add(permission)
            admin_group.permissions.add(admin_permission)
    for admin_user in admin_users_:
        if admin_user not in admin_users:
            admin_user.user_permissions.add(permission)
            admin_user.user_permissions.add(admin_permission)


# pylint: enable=too-many-arguments
# pylint: enable=too-many-branches


@auth_login_required()
@user_passes_test(lambda u: u.is_staff)
def del_meetingtype(request: AuthWSGIRequest, mt_pk: str) -> HttpResponse:
    meetingtype: MeetingType = get_object_or_404(MeetingType, pk=mt_pk)
    form = forms.Form(request.POST or None)
    if form.is_valid():
        meetingtype.delete()

        return redirect("meetingtypes:list_meetingtypes")

    context = {
        "meetingtype": meetingtype,
        "form": form,
    }
    return render(request, "meetingtypes/del.html", context)


# show upcoming meetings for one meetingtype (allowed only by users with
# permission for that meetingtype or allowed for public if public-bit set)
@xframe_options_exempt
def upcoming_meetings(request: WSGIRequest, mt_pk: str) -> HttpResponse:
    meetingtype: MeetingType = get_object_or_404(MeetingType, pk=mt_pk)
    if not meetingtype.public:  # public access disabled
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not request.user.has_perm(meetingtype.permission()):
            raise PermissionDenied

    context = {
        "meetingtype": meetingtype,
        "upcoming_meetings": meetingtype.upcoming_meetings,
    }
    return render(request, "meetingtypes/upcoming.html", context)
