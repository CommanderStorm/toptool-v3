from collections import OrderedDict
from typing import Optional

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
from tops.models import Top
from toptool.utils.permission import auth_login_required
from toptool.utils.shortcuts import get_permitted_mts_sorted, render
from toptool.utils.typing import AuthWSGIRequest

from .forms import MTAddForm, MTForm
from .models import MeetingType


def list_meetingtypes(request: WSGIRequest) -> HttpResponse:
    """
    Lists all meetingtypes the user is a member of, if logged-in else a page requesting a log-in.

    @permission: allowed only by anyone
    @param request: a WSGIRequest
    @return: a HttpResponse
    """

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
    return render(request, "meetingtypes/list_meetingtypes.html", context)


@auth_login_required()
@user_passes_test(lambda u: u.is_staff)
def list_meetingtypes_admin(request: AuthWSGIRequest) -> HttpResponse:
    """
    Admin interface: view all meetingtypes.

    @permission: allowed only by staff
    @param request: a WSGIRequest by a logged-in user
    @return: a HttpResponse
    """

    all_meetingtypes = MeetingType.objects.order_by("name")
    context = {
        "all_meetingtypes": all_meetingtypes,
    }
    return render(request, "meetingtypes/list_meetingtypes_admin.html", context)


@auth_login_required()
@user_passes_test(lambda u: u.is_staff)
def list_admins(request: AuthWSGIRequest) -> HttpResponse:
    """
    List all email addresses of admins and meetingtype admins.

    @permission: allowed only by staff
    @param request: a WSGIRequest by a logged-in user
    @return: a HttpResponse
    """

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
    return render(request, "meetingtypes/list_admins.html", context)


def search_meetingtype_archive(request: WSGIRequest, mt_pk: str, year: int) -> HttpResponse:
    """
    Searches the meeting archive for given year.

    @permission: allowed only by users with permission for that meetingtype or allowed for public if public-bit set
    @param request: a WSGIRequest
    @param mt_pk: id of a MeetingType
    @param year: the given year
    @return: a HttpResponse
    """

    return _view_meetingtype_archive(request, mt_pk, year, search_archive_flag=True)


def view_meetingtype_archive(request: WSGIRequest, mt_pk: str, year: int) -> HttpResponse:
    """
    Shows meeting archive for given year (possibly searching it).

    @permission: allowed only by users with permission for that meetingtype or allowed for public if public-bit set
    @param request: a WSGIRequest
    @param mt_pk: id of a MeetingType
    @param year: the given year
    @return: a HttpResponse
    """

    return _view_meetingtype_archive(request, mt_pk, year, search_archive_flag=False)


def search_meetingtype(request: WSGIRequest, mt_pk: str) -> HttpResponse:
    """
    Searches a meetingtype.

    @permission: allowed only by users with permission for that meetingtype or allowed for public if public-bit set
    @param request: a WSGIRequest
    @param mt_pk: id of a MeetingType
    @return: a HttpResponse
    """

    return _view_meetingtype(request, mt_pk, search_mt=True)


def view_meetingtype(request: WSGIRequest, mt_pk: str) -> HttpResponse:
    """
    Shows single meetingtype.

    @permission: allowed only by users with permission for that meetingtype or allowed for public if public-bit set
    @param request: a WSGIRequest
    @param mt_pk: id of a MeetingType
    @return: a HttpResponse
    """

    return _view_meetingtype(request, mt_pk, search_mt=False)


def _get_query_string(request: WSGIRequest) -> str:
    """
    Get the query_string, if present in the POST or GET request, else ""

    @param request: a WSGIRequest
    @return: a possibly blank query_string
    """

    return request.POST.get("query", default="") or request.GET.get("query", default="")


def _search_meeting(request: WSGIRequest, meeting: Meeting, search_query: str) -> list[str]:
    location = []
    top_set: list[Top] = list(meeting.top_set.order_by("topid").all())
    for top in top_set:
        if search_query.lower() in top.title.lower() or search_query.lower() in top.description.lower():
            location.append("Tagesordnung")
            break
    try:
        protokoll: Optional[Protokoll] = meeting.protokoll
    except Protokoll.DoesNotExist:
        protokoll = None
    if protokoll and protokoll.filepath:
        privileged_user = (
            request.user.has_perm(meeting.meetingtype.admin_permission())
            or request.user == meeting.sitzungsleitung
            or request.user in meeting.minute_takers.all()
        )
        if (protokoll.published or privileged_user) and (protokoll.approved or request.user.is_authenticated):
            with open(protokoll.filepath + ".txt", "r", encoding="UTF-8") as file:
                content = file.read()
                if search_query.lower() in content.lower():
                    location.append("Protokoll")
    return location


def _search_meetings_qs(
    request: WSGIRequest,
    meetings: QuerySet[Meeting],
    search_query: str,
) -> OrderedDict[Meeting, list[str]]:
    meeting_location = OrderedDict()
    meeting: Meeting
    for meeting in meetings:
        location: list[str] = []
        # check for substring in the title
        title: str = meeting.title
        if not title:
            title = meeting.meetingtype.defaultmeetingtitle
        if search_query.lower() in title.lower():
            location.append("Titel")
        # check for substring in any of the TOPs or the minutes
        location.extend(_search_meeting(request, meeting, search_query))

        if location:
            meeting_location[meeting] = location
    return meeting_location


def _view_meetingtype(request: WSGIRequest, mt_pk: str, search_mt: bool) -> HttpResponse:
    """
    Shows single meetingtype (possibly searching it).

    @permission: allowed only by users with permission for that meetingtype or allowed for public if public-bit set
    @param request: a WSGIRequest
    @param mt_pk: id of a MeetingType
    @param search_mt: flag determining if the meetingtype should be searched
    @return: a HttpResponse
    """

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
    search_query: str = _get_query_string(request)
    if search_mt:
        if not search_query:
            return redirect("meetingtypes:view_meetingtype", mt_pk)
        past_meetings_dict: OrderedDict[Meeting, list[str]] = _search_meetings_qs(
            request,
            past_meetings_qs,
            search_query,
        )
        upcoming_meetings_dict: OrderedDict[Meeting, list[str]] = _search_meetings_qs(
            request,
            upcoming_meetings_qs,
            search_query,
        )
    else:
        # OrderedDict.fromkeys returns a OrderedDict and not a dict, as mypy thinks
        past_meetings_dict = OrderedDict.fromkeys(past_meetings_qs, [])  # type: ignore
        upcoming_meetings_dict = OrderedDict.fromkeys(upcoming_meetings_qs, [])  # type: ignore

    prev_year, next_year = _get_surrounding_years(years, year)

    ical_url = None
    if meetingtype.ical_key:
        relative_ical_url = reverse("meetingtypes:ical_meeting_feed", args=[meetingtype.pk, meetingtype.ical_key])
        ical_url = request.build_absolute_uri(relative_ical_url)

    context = {
        "meetingtype": meetingtype,
        "years": years,
        "current": year,
        "prev": prev_year,
        "next": next_year,
        "ical_url": ical_url,
        "past_meetings": past_meetings_dict,
        "upcoming_meetings": upcoming_meetings_dict,
        "search_query": search_query,
        "search": search_mt,
    }
    return render(request, "meetingtypes/view_meetingtype.html", context)


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


def _view_meetingtype_archive(request: WSGIRequest, mt_pk: str, year: int, search_archive_flag: bool) -> HttpResponse:
    """
    Shows meeting archive for given year (possibly searching it).

    @permission: allowed only by users with permission for that meetingtype or allowed for public if public-bit set
    @param request: a WSGIRequest
    @param mt_pk: id of a MeetingType
    @param year: the given year
    @param search_archive_flag: flag determining if the meeting archive should be searched
    @return: a HttpResponse
    """
    if not 1950 < year < 2050:
        raise Http404("Invalid year. Asserted to be between 1950 and 2050")
    meetingtype: MeetingType = get_object_or_404(MeetingType, pk=mt_pk)
    if not meetingtype.public:  # public access disabled
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not request.user.has_perm(meetingtype.permission()):
            raise PermissionDenied

    search_query: str = _get_query_string(request)

    if year >= timezone.now().year:
        # the user has modified the url to be too far in the future. Timetraveling is not allowed
        # Thus, we reset to the present :)
        messages.error(request, _("Unsere Zeitmaschiene ist momentan kaputt. versuche es bitte später."))
        return redirect("meetingtypes:view_meetingtype", mt_pk)

    meetings_qs: QuerySet[Meeting] = meetingtype.past_meetings_by_year(year)
    years: list[int] = [year for year in meetingtype.years if year <= timezone.now().year]

    if search_archive_flag:
        if not search_query:
            return redirect("meetingtypes:view_archive", mt_pk, year)
        meetings: OrderedDict[Meeting, list[str]] = _search_meetings_qs(request, meetings_qs, search_query)
    else:
        # OrderedDict.fromkeys returns a OrderedDict and not a dict, as mypy thinks
        meetings = OrderedDict.fromkeys(meetings_qs, [])  # type: ignore

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
    return render(request, "meetingtypes/view_meetingtype_archive.html", context)


@auth_login_required()
@user_passes_test(lambda u: u.is_staff)
def add_meetingtype(request: AuthWSGIRequest) -> HttpResponse:
    """
    Create a new meetingtype.

    @permission: allowed only by staff
    @param request: a WSGIRequest by a logged-in user
    @return: a HttpResponse
    """

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
    return render(request, "meetingtypes/edit_meetingtype.html", context)


@auth_login_required()
def edit_meetingtype(request: AuthWSGIRequest, mt_pk: str) -> HttpResponse:
    """
    Edits a given meetingtype.

    @permission: allowed only by meetingtype-admin or staff
    @param request: a WSGIRequest by a logged-in user
    @param mt_pk: id of a MeetingType
    @return: a HttpResponse
    """

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
    return render(request, "meetingtypes/edit_meetingtype.html", context)


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
    """
    Deletes a given meetingtype.

    @permission: allowed only by tool-admin or staff
    @param request: a WSGIRequest by a logged-in user
    @param mt_pk: id of a MeetingType
    @return: a HttpResponse
    """

    meetingtype: MeetingType = get_object_or_404(MeetingType, pk=mt_pk)
    form = forms.Form(request.POST or None)
    if form.is_valid():
        meetingtype.delete()

        return redirect("meetingtypes:list_meetingtypes")

    context = {
        "meetingtype": meetingtype,
        "form": form,
    }
    return render(request, "meetingtypes/del_meetingtype.html", context)


@xframe_options_exempt
def upcoming_meetings(request: WSGIRequest, mt_pk: str) -> HttpResponse:
    """
    Shows upcoming meetings for one meetingtype.

    @permission: allowed only by users with permission for that meetingtype or allowed for public if public-bit set
    @param request: a WSGIRequest
    @param mt_pk: id of a MeetingType
    @return: a HttpResponse
    """
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
    return render(request, "meetingtypes/upcoming_meetings.html", context)
