from typing import Any, Dict
from uuid import UUID

from django import forms
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.handlers.wsgi import WSGIRequest
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.clickjacking import xframe_options_exempt

from meetings.models import Meeting
from meetingtypes.models import MeetingType
from toptool.utils.files import prep_file
from toptool.utils.helpers import get_meeting_or_404_on_validation_error
from toptool.utils.permission import auth_login_required, is_admin_sitzungsleitung, is_admin_staff, require
from toptool.utils.shortcuts import render
from toptool.utils.typing import AuthWSGIRequest

from .forms import AddStdForm, AddTopForm, EditStdForm, EditTopForm
from .models import StandardTop, Top


@auth_login_required()
def view_tops(request: AuthWSGIRequest, meeting_pk: UUID) -> HttpResponse:
    """
    Edits the list of tops of a given meeting.

    @permission: allowed only by meetingtype-admin and sitzungsleitung
    @param request: a WSGIRequest by a logged-in user
    @param meeting_pk: uuid of a Meeting
    @return: a HttpResponse
    """

    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)

    require(is_admin_sitzungsleitung(request, meeting))
    require(not meeting.imported)

    if not meeting.meetingtype.tops:
        raise Http404

    meeting_tops = meeting.tops_with_id

    context = {
        "meeting": meeting,
        "tops": meeting_tops,
    }
    return render(request, "tops/list.html", context)


@auth_login_required()
def sort_tops(request: AuthWSGIRequest, meeting_pk: UUID) -> HttpResponse:
    """
    Enables the user to sort the tops of a given meeting.

    @permission: allowed only by meetingtype-admin and sitzungsleitung
    @param request: a WSGIRequest by a logged-in user
    @param meeting_pk: uuid of a Meeting
    @return: a HttpResponse
    """

    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)

    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or request.user == meeting.sitzungsleitung):
        raise PermissionDenied
    require(not meeting.imported)

    if not meeting.meetingtype.tops:
        raise Http404

    if request.method == "POST":
        tops = request.POST.getlist("tops[]")
        tops = [t for t in tops if t]
        if tops:
            for counter, top_id in enumerate(tops):
                try:
                    top_pk = top_id.partition("_")[2]
                except IndexError:
                    return HttpResponseBadRequest()
                try:
                    top = Top.objects.get(pk=top_pk)
                except (Top.DoesNotExist, ValidationError):
                    return HttpResponseBadRequest()
                if top.topid < 10000:
                    top.topid = counter + 1
                    top.save()
            return JsonResponse({"success": True})

    return HttpResponseBadRequest()


@xframe_options_exempt
def list_tops(request: WSGIRequest, meeting_pk: UUID) -> HttpResponse:
    """
    Lists all tops of a meeting.
    This is used to embed the tops in the homepage.

    @permission: allowed only by users with permission for the meetingtype or allowed for public if public-bit set
    @param request: a WSGIRequest
    @param meeting_pk: uuid of a Meeting
    @return: a HttpResponse
    """

    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)

    if not meeting.meetingtype.public:  # public access disabled
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not request.user.has_perm(meeting.meetingtype.permission()):
            raise PermissionDenied
    require(not meeting.imported)

    if not meeting.meetingtype.tops:
        raise Http404

    tops = meeting.tops_with_id

    context = {
        "meeting": meeting,
        "tops": tops,
    }
    return render(request, "tops/view.html", context)


@xframe_options_exempt
def next_meeting_nonexistant(request: WSGIRequest, mt_pk: str) -> HttpResponse:
    """
    Shows that there don't exist any next meetings.

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

    if not meetingtype.tops:
        raise Http404

    context = {"meetingtype": meetingtype}
    return render(request, "tops/nonext.html", context)


@auth_login_required()
def del_top(request: AuthWSGIRequest, top_pk: UUID) -> HttpResponse:
    """
    Deletes a given TOP.

    @permission: allowed only by meetingtype-admin and sitzungsleitung
    @param request: a WSGIRequest by a logged-in user
    @param top_pk: uuid of a TOP
    @return: a HttpResponse
    """

    try:
        top: Top = get_object_or_404(Top, pk=top_pk)
    except ValidationError as error:
        raise Http404 from error
    meeting: Meeting = top.meeting
    if not meeting.meetingtype.tops:
        raise Http404
    if not (
        request.user.has_perm(meeting.meetingtype.admin_permission())
        or request.user == meeting.sitzungsleitung
        or (
            meeting.meetingtype.top_user_edit
            and not meeting.topdeadline_over
            and request.user.has_perm(meeting.meetingtype.permission())
            and request.user == top.user
        )
    ):
        raise PermissionDenied
    require(not meeting.imported)

    form = forms.Form(request.POST or None)
    if form.is_valid():
        meeting.top_set.filter(pk=top_pk).delete()

        return redirect("meetings:view_meeting", meeting.id)

    context = {
        "meeting": meeting,
        "top": top,
        "form": form,
    }
    return render(request, "tops/del.html", context)


def show_attachment(request: WSGIRequest, top_pk: UUID) -> HttpResponse:
    """
    Shows the attachment of a given TOP.

    @permission: allowed only by users with permission for the meetingtype or allowed for public if public-bit set
    @param request: a WSGIRequest
    @param top_pk: uuid of a TOP
    @return: a HttpResponse
    """

    try:
        top: Top = get_object_or_404(Top, pk=top_pk)
    except ValidationError as error:
        raise Http404 from error

    meeting: Meeting = top.meeting
    if not meeting.meetingtype.public:
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not request.user.has_perm(meeting.meetingtype.permission()):
            raise PermissionDenied
    require(not meeting.imported)

    if not meeting.meetingtype.tops or not meeting.meetingtype.attachment_tops:
        raise Http404

    return prep_file(top.attachment.path)


def add_top(request: WSGIRequest, meeting_pk: UUID) -> HttpResponse:
    """
    Add a new top.

    @permission: allowed only by users with permission for the meetingtype or for the public if public-bit is set
    @param request: a WSGIRequest by a logged-in user
    @param meeting_pk: uuid of a Meeting
    @return: a HttpResponse
    """

    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)
    if (
        meeting.meetingtype.top_perms == "public" and not meeting.meetingtype.public
    ) or meeting.meetingtype.top_perms == "perm":
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        require(request.user.has_perm(meeting.meetingtype.permission()))
    elif meeting.meetingtype.top_perms == "admin":
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        require(is_admin_sitzungsleitung(request, meeting))
    require(not meeting.imported)

    if not meeting.meetingtype.tops:
        raise Http404

    if (
        meeting.topdeadline_over
        and request.user != meeting.sitzungsleitung
        and not request.user.has_perm(meeting.meetingtype.admin_permission())
    ):
        context: Dict[str, Any] = {
            "meeting": meeting,
            "form": None,
        }
        return render(request, "tops/add.html", context)

    initial = {}
    authenticated = False
    if request.user.is_authenticated:
        initial["author"] = request.user.first_name + " " + request.user.last_name
        initial["email"] = request.user.email
        authenticated = True

    form = AddTopForm(
        request.POST or None,
        request.FILES or None,
        meeting=meeting,
        initial=initial,
        authenticated=authenticated,
    )
    if form.is_valid():
        top = form.save()
        access_permitted = request.user.has_perm(meeting.meetingtype.permission())
        if request.user.is_authenticated and access_permitted:
            top.user = request.user
            top.save()
        return redirect("meetings:view_meeting", meeting.id)

    context = {
        "meeting": meeting,
        "form": form,
    }
    return render(request, "tops/add.html", context)


@auth_login_required()
def edit_top(request: AuthWSGIRequest, top_pk: UUID) -> HttpResponse:
    """
    Edits a given TOP.

    @permission: allowed only by meetingtype-admin and sitzungsleitung
    @param request: a WSGIRequest by a logged-in user
    @param top_pk: uuid of a TOP
    @return: a HttpResponse
    """

    try:
        top: Top = get_object_or_404(Top, pk=top_pk)
    except ValidationError as error:
        raise Http404 from error
    meeting: Meeting = top.meeting

    if not meeting.meetingtype.tops:
        raise Http404
    if not (
        request.user.has_perm(meeting.meetingtype.admin_permission())
        or request.user == meeting.sitzungsleitung
        or (
            meeting.meetingtype.top_user_edit
            and not meeting.topdeadline_over
            and request.user.has_perm(meeting.meetingtype.permission())
            and request.user == top.user
        )
    ):
        raise PermissionDenied
    require(not meeting.imported)

    user_edit = False
    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or request.user == meeting.sitzungsleitung):
        user_edit = True

    form = EditTopForm(
        request.POST or None,
        request.FILES or None,
        instance=top,
        user_edit=user_edit,
    )
    if form.is_valid():
        form.save()
        return redirect("meetings:view_meeting", meeting.id)

    context = {
        "meeting": meeting,
        "top": top,
        "form": form,
    }
    return render(request, "tops/edit.html", context)


@auth_login_required()
def del_stdtop(request: AuthWSGIRequest, top_pk: UUID) -> HttpResponse:
    """
    Deletes a given standard-TOP.

    @permission: allowed only by meetingtype-admin and sitzungsleitung
    @param request: a WSGIRequest by a logged-in user
    @param stdtop_pk: uuid of the standard-top
    @return: a HttpResponse
    """

    try:
        standardtop: StandardTop = get_object_or_404(StandardTop, pk=top_pk)
    except ValidationError as error:
        raise Http404 from error
    meetingtype: MeetingType = standardtop.meetingtype
    require(is_admin_staff(request, meetingtype))

    if not meetingtype.tops or not meetingtype.standard_tops:
        raise Http404

    form = forms.Form(request.POST or None)
    if form.is_valid():
        meetingtype.standardtop_set.filter(pk=top_pk).delete()

        return redirect("tops:list_stdtops", meetingtype.id)

    context = {
        "meetingtype": meetingtype,
        "standardtop": standardtop,
        "form": form,
    }
    return render(request, "tops/del_std.html", context)


@auth_login_required()
def add_stdtop(request: AuthWSGIRequest, mt_pk: str) -> HttpResponse:
    """
    Creates a new standard top for a meetingtype.

    @permission: allowed only by meetingtype-admin and staff
    @param request: a WSGIRequest by a logged-in user
    @param mt_pk: id of a MeetingType
    @return: a HttpResponse
    """

    meetingtype: MeetingType = get_object_or_404(MeetingType, pk=mt_pk)
    require(is_admin_staff(request, meetingtype))

    if not meetingtype.tops or not meetingtype.standard_tops:
        raise Http404

    form = AddStdForm(request.POST or None, meetingtype=meetingtype)
    if form.is_valid():
        form.save()

        return redirect("tops:list_stdtops", meetingtype.id)

    context = {
        "meetingtype": meetingtype,
        "form": form,
    }
    return render(request, "tops/add_std.html", context)


@auth_login_required()
def edit_stdtop(request: AuthWSGIRequest, top_pk: UUID) -> HttpResponse:
    """
    Edits a given standard-TOP.

    @permission: allowed only by meetingtype-admin and sitzungsleitung
    @param request: a WSGIRequest by a logged-in user
    @param stdtop_pk: uuid of the standard-TOP
    @return: a HttpResponse
    """

    try:
        standardtop: StandardTop = get_object_or_404(StandardTop, pk=top_pk)
    except ValidationError as error:
        raise Http404 from error

    meetingtype: MeetingType = standardtop.meetingtype
    require(is_admin_staff(request, meetingtype))

    if not meetingtype.tops or not meetingtype.standard_tops:
        raise Http404
    form = EditStdForm(request.POST or None, instance=standardtop)
    if form.is_valid():
        form.save()

        return redirect("tops:list_stdtops", meetingtype.id)

    context = {
        "meetingtype": meetingtype,
        "standardtop": standardtop,
        "form": form,
    }
    return render(request, "tops/edit_std.html", context)


@auth_login_required()
def list_stdtops(request: AuthWSGIRequest, mt_pk: str) -> HttpResponse:
    """
    Lists all standard tops of a meetingtype.

    @permission: allowed only by meetingtype-admin or staff
    @param request: a WSGIRequest by a logged-in user
    @param mt_pk: id of a MeetingType
    @return: a HttpResponse
    """

    meetingtype: MeetingType = get_object_or_404(MeetingType, pk=mt_pk)
    require(is_admin_staff(request, meetingtype))

    if not meetingtype.tops or not meetingtype.standard_tops:
        raise Http404

    standardtops = meetingtype.standardtop_set.order_by("topid")

    context = {
        "meetingtype": meetingtype,
        "standardtops": standardtops,
    }
    return render(request, "tops/list_std.html", context)


@auth_login_required()
def sort_stdtops(request: AuthWSGIRequest, mt_pk: str) -> HttpResponse:
    """
    Modifys the sorting of standard tops of a meetingtype.

    @permission: allowed only by meetingtype-admin or staff
    @param request: a WSGIRequest by a logged-in user
    @param mt_pk: id of a MeetingType
    @return: a HttpResponse
    """

    meetingtype: MeetingType = get_object_or_404(MeetingType, pk=mt_pk)
    require(is_admin_staff(request, meetingtype))

    if not meetingtype.tops or not meetingtype.standard_tops:
        raise Http404

    if request.method == "POST":
        tops = request.POST.getlist("tops[]")
        tops = [t for t in tops if t]
        if tops:
            for counter, top_id in enumerate(tops):
                try:
                    standard_top_pk = top_id.partition("_")[2]
                except IndexError:
                    return HttpResponseBadRequest()
                try:
                    top = StandardTop.objects.get(pk=standard_top_pk)
                except (StandardTop.DoesNotExist, ValidationError):
                    return HttpResponseBadRequest()
                top.topid = counter + 1
                top.save()
            return JsonResponse({"success": True})
    return HttpResponseBadRequest()
