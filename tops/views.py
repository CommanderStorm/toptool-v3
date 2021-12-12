from typing import Any, Dict
from uuid import UUID
from wsgiref.util import FileWrapper

import magic
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
from toptool.utils.helpers import get_meeting_or_404_on_validation_error
from toptool.utils.permission import auth_login_required, is_admin_sitzungsleitung, is_admin_staff, require
from toptool.utils.shortcuts import render
from toptool.utils.typing import AuthWSGIRequest

from .forms import AddForm, AddStdForm, EditForm, EditStdForm
from .models import StandardTop, Top


# edit list of tops (allowed only by meetingtype-admin and sitzungsleitung)
@auth_login_required()
def edit_tops(request: AuthWSGIRequest, mt_pk: str, meeting_pk: UUID) -> HttpResponse:
    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)

    require(is_admin_sitzungsleitung(request, meeting))
    require(not meeting.imported)

    if not meeting.meetingtype.tops:
        raise Http404

    meeting_tops = meeting.get_tops_with_id()

    context = {
        "meeting": meeting,
        "tops": meeting_tops,
    }
    return render(request, "tops/list.html", context)


# sort tops (allowed only by meetingtype-admin and sitzungsleitung)
@auth_login_required()
def sort_tops(request: AuthWSGIRequest, mt_pk: str, meeting_pk: UUID) -> HttpResponse:
    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)

    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or request.user == meeting.sitzungsleitung):
        raise PermissionDenied
    require(not meeting.imported)

    if not meeting.meetingtype.tops:
        raise Http404

    if request.method == "POST":
        tops = request.POST.getlist("tops[]", None)
        tops = [t for t in tops if t]
        if tops:
            for counter, top_id in enumerate(tops):
                try:
                    top_pk = top_id.partition("_")[2]
                except IndexError:
                    return HttpResponseBadRequest("")
                try:
                    top = Top.objects.get(pk=top_pk)
                except (Top.DoesNotExist, ValidationError):
                    return HttpResponseBadRequest("")
                if top.topid < 10000:
                    top.topid = counter + 1
                    top.save()
            return JsonResponse({"success": True})

    return HttpResponseBadRequest("")


# list of tops for a meeting (allowed only by users with permission for the
# meetingtype or allowed for public if public-bit set)
# this is only used to embed the tops in the homepage
@xframe_options_exempt
def list_tops(request: WSGIRequest, mt_pk: str, meeting_pk: UUID) -> HttpResponse:
    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)

    if not meeting.meetingtype.public:  # public access disabled
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not request.user.has_perm(meeting.meetingtype.permission()):
            raise PermissionDenied
    require(not meeting.imported)

    if not meeting.meetingtype.tops:
        raise Http404

    tops = meeting.get_tops_with_id()

    context = {
        "meeting": meeting,
        "tops": tops,
    }
    return render(request, "tops/view.html", context)


# show that there exists no next meeting
@xframe_options_exempt
def nonext(request: WSGIRequest, mt_pk: str) -> HttpResponse:
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


# delete given top (allowed only by meetingtype-admin and sitzungsleitung)
@auth_login_required()
def delete_top(
    request: AuthWSGIRequest,
    mt_pk: str,
    meeting_pk: UUID,
    top_pk: UUID,
) -> HttpResponse:
    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)
    if not meeting.meetingtype.tops:
        raise Http404
    try:
        top = get_object_or_404(meeting.top_set, pk=top_pk)
    except ValidationError as error:
        raise Http404 from error
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

        return redirect("viewmeeting", meeting.meetingtype.id, meeting.id)

    context = {
        "meeting": meeting,
        "top": top,
        "form": form,
    }
    return render(request, "tops/del.html", context)


# show top attachment (allowed only by users with permission for the
# meetingtype or allowed for public if public-bit set)
def show_attachment(
    request: WSGIRequest,
    mt_pk: str,
    meeting_pk: UUID,
    top_pk: UUID,
) -> HttpResponse:
    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)
    if not meeting.meetingtype.public:
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not request.user.has_perm(meeting.meetingtype.permission()):
            raise PermissionDenied
    require(not meeting.imported)

    if not meeting.meetingtype.tops or not meeting.meetingtype.attachment_tops:
        raise Http404

    try:
        top = get_object_or_404(meeting.top_set, pk=top_pk)
    except ValidationError as error:
        raise Http404 from error
    filename = top.attachment.path
    with open(filename, "rb") as file:
        filetype = magic.from_buffer(file.read(1024), mime=True)
    with open(filename, "rb") as file:
        wrapper = FileWrapper(file)
        return HttpResponse(wrapper, content_type=filetype)


# add new top (allowed only by users with permission for the meetingtype or
# allowed for public if public-bit set)
def add_top(request: WSGIRequest, mt_pk: str, meeting_pk: UUID) -> HttpResponse:
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

    form = AddForm(
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
        return redirect("viewmeeting", meeting.meetingtype.id, meeting.id)

    context = {
        "meeting": meeting,
        "form": form,
    }
    return render(request, "tops/add.html", context)


# edit given top (allowed only by meetingtype-admin and sitzungsleitung)
@auth_login_required()
def edit_top(
    request: AuthWSGIRequest,
    mt_pk: str,
    meeting_pk: UUID,
    top_pk: UUID,
) -> HttpResponse:
    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)

    if not meeting.meetingtype.tops:
        raise Http404
    try:
        top = get_object_or_404(meeting.top_set, pk=top_pk)
    except ValidationError as error:
        raise Http404 from error
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

    form = EditForm(
        request.POST or None,
        request.FILES or None,
        instance=top,
        user_edit=user_edit,
    )
    if form.is_valid():
        form.save()
        return redirect("viewmeeting", meeting.meetingtype.id, meeting.id)

    context = {
        "meeting": meeting,
        "top": top,
        "form": form,
    }
    return render(request, "tops/edit.html", context)


# delete standard top (allowed only by meetingtype-admin and staff)
@auth_login_required()
def delete_std(request: AuthWSGIRequest, mt_pk: str, top_pk: UUID) -> HttpResponse:
    meetingtype: MeetingType = get_object_or_404(MeetingType, pk=mt_pk)
    require(is_admin_staff(request, meetingtype))

    if not meetingtype.tops or not meetingtype.standard_tops:
        raise Http404

    try:
        standardtop = get_object_or_404(meetingtype.standardtop_set, pk=top_pk)
    except ValidationError as error:
        raise Http404 from error

    form = forms.Form(request.POST or None)
    if form.is_valid():
        meetingtype.standardtop_set.filter(pk=top_pk).delete()

        return redirect("liststdtops", meetingtype.id)

    context = {
        "meetingtype": meetingtype,
        "standardtop": standardtop,
        "form": form,
    }
    return render(request, "tops/del_std.html", context)


# add new standard top (allowed only by meetingtype-admin and staff)
@auth_login_required()
def add_std(request: AuthWSGIRequest, mt_pk: str) -> HttpResponse:
    meetingtype: MeetingType = get_object_or_404(MeetingType, pk=mt_pk)
    require(is_admin_staff(request, meetingtype))

    if not meetingtype.tops or not meetingtype.standard_tops:
        raise Http404

    form = AddStdForm(request.POST or None, meetingtype=meetingtype)
    if form.is_valid():
        form.save()

        return redirect("liststdtops", meetingtype.id)

    context = {
        "meetingtype": meetingtype,
        "form": form,
    }
    return render(request, "tops/add_std.html", context)


# edit standard top (allowed only by meetingtype-admin and staff)
@auth_login_required()
def edit_std(request: AuthWSGIRequest, mt_pk: str, top_pk: UUID) -> HttpResponse:
    meetingtype: MeetingType = get_object_or_404(MeetingType, pk=mt_pk)
    require(is_admin_staff(request, meetingtype))

    if not meetingtype.tops or not meetingtype.standard_tops:
        raise Http404

    try:
        standardtop = get_object_or_404(meetingtype.standardtop_set, pk=top_pk)
    except ValidationError as error:
        raise Http404 from error

    form = EditStdForm(request.POST or None, instance=standardtop)
    if form.is_valid():
        form.save()

        return redirect("liststdtops", meetingtype.id)

    context = {
        "meetingtype": meetingtype,
        "standardtop": standardtop,
        "form": form,
    }
    return render(request, "tops/edit_std.html", context)


# list of standard tops (allowed only by meetingtype-admin or staff)
@auth_login_required()
def stdtops(request: AuthWSGIRequest, mt_pk: str) -> HttpResponse:
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


# sort standard tops (allowed only by meetingtype-admin or staff)
@auth_login_required()
def sort_stdtops(request: AuthWSGIRequest, mt_pk: str) -> HttpResponse:
    meetingtype: MeetingType = get_object_or_404(MeetingType, pk=mt_pk)
    require(is_admin_staff(request, meetingtype))

    if not meetingtype.tops or not meetingtype.standard_tops:
        raise Http404

    if request.method == "POST":
        tops = request.POST.getlist("tops[]", None)
        tops = [t for t in tops if t]
        if tops:
            for counter, top_id in enumerate(tops):
                try:
                    standard_top_pk = top_id.partition("_")[2]
                except IndexError:
                    return HttpResponseBadRequest("")
                try:
                    top = StandardTop.objects.get(pk=standard_top_pk)
                except (StandardTop.DoesNotExist, ValidationError):
                    return HttpResponseBadRequest("")
                top.topid = counter + 1
                top.save()
            return JsonResponse({"success": True})
    return HttpResponseBadRequest()
