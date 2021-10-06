from uuid import UUID
from wsgiref.util import FileWrapper

import magic
from django import forms
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseBadRequest, HttpResponse, Http404
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.clickjacking import xframe_options_exempt

from meetings.models import Meeting
from meetingtypes.models import MeetingType
from toptool.shortcuts import render
from .forms import AddForm, EditForm, AddStdForm, EditStdForm
from .models import Top, StandardTop


# edit list of tops (allowed only by meetingtype-admin and sitzungsleitung)
@login_required
def tops(request: WSGIRequest, mt_pk: str, meeting_pk: UUID) -> HttpResponse:
    try:
        meeting = get_object_or_404(Meeting, pk=meeting_pk)
    except ValidationError:
        raise Http404

    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung):
        raise PermissionDenied
    if meeting.imported:
        raise PermissionDenied

    if not meeting.meetingtype.tops:
        raise Http404

    tops = meeting.get_tops_with_id()

    context = {
        'meeting': meeting,
        'tops': tops,
    }
    return render(request, 'tops/list.html', context)


# sort tops (allowed only by meetingtype-admin and sitzungsleitung)
@login_required
def sort_tops(request: WSGIRequest, mt_pk: str, meeting_pk: UUID) -> HttpResponse:
    try:
        meeting = get_object_or_404(Meeting, pk=meeting_pk)
    except ValidationError:
        raise Http404

    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung):
        raise PermissionDenied
    if meeting.imported:
        raise PermissionDenied

    if not meeting.meetingtype.tops:
        raise Http404

    if request.method == "POST":
        tops = request.POST.getlist("tops[]", None)
        tops = [t for t in tops if t]
        if tops:
            for i, t in enumerate(tops):
                try:
                    pk = t.partition("_")[2]
                except IndexError:
                    return HttpResponseBadRequest('')
                try:
                    top = Top.objects.get(pk=pk)
                except (Top.DoesNotExist, ValidationError):
                    return HttpResponseBadRequest('')
                if top.topid < 10000:
                    top.topid = i+1
                    top.save()
            return JsonResponse({'success': True})

    return HttpResponseBadRequest('')


# list of tops for a meeting (allowed only by users with permission for the
# meetingtype or allowed for public if public-bit set)
# this is only used to embed the tops in the homepage
@xframe_options_exempt
def list_tops(request: WSGIRequest, mt_pk: str, meeting_pk: UUID) -> HttpResponse:
    try:
        meeting = get_object_or_404(Meeting, pk=meeting_pk)
    except ValidationError:
        raise Http404

    if not meeting.meetingtype.public:          # public access disabled
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        if not request.user.has_perm(meeting.meetingtype.permission()):
            raise PermissionDenied
    if meeting.imported:
        raise PermissionDenied

    if not meeting.meetingtype.tops:
        raise Http404

    tops = meeting.get_tops_with_id()

    context = {'meeting': meeting,
               'tops': tops}
    return render(request, 'tops/view.html', context)


# show that there exists no next meeting
@xframe_options_exempt
def nonext(request: WSGIRequest, mt_pk: str) -> HttpResponse:
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    if not meetingtype.public:          # public access disabled
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        if not request.user.has_perm(meetingtype.permission()):
            raise PermissionDenied

    if not meetingtype.tops:
        raise Http404

    context = {'meetingtype': meetingtype}
    return render(request, 'tops/nonext.html', context)


# delete given top (allowed only by meetingtype-admin and sitzungsleitung)
@login_required
def delete(request: WSGIRequest, mt_pk: str, meeting_pk, top_pk) -> HttpResponse:
    try:
        meeting = get_object_or_404(Meeting, pk=meeting_pk)
    except ValidationError:
        raise Http404
    if not meeting.meetingtype.tops:
        raise Http404
    try:
        top = get_object_or_404(meeting.top_set, pk=top_pk)
    except ValidationError:
        raise Http404
    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung or
            (meeting.meetingtype.top_user_edit and not meeting.topdeadline_over
                and request.user.has_perm(meeting.meetingtype.permission())
                and request.user == top.user)):
        raise PermissionDenied
    elif meeting.imported:
        raise PermissionDenied

    form = forms.Form(request.POST or None)
    if form.is_valid():
        meeting.top_set.filter(pk=top_pk) .delete()

        return redirect('viewmeeting', meeting.meetingtype.id, meeting.id)

    context = {'meeting': meeting,
               'top': top,
               'form': form}
    return render(request, 'tops/del.html', context)


# show top attachment (allowed only by users with permission for the
# meetingtype or allowed for public if public-bit set)
def show_attachment(request: WSGIRequest, mt_pk: str, meeting_pk, top_pk) -> HttpResponse:
    try:
        meeting = get_object_or_404(Meeting, pk=meeting_pk)
    except ValidationError:
        raise Http404
    if not meeting.meetingtype.public:
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        if not request.user.has_perm(meeting.meetingtype.permission()):
            raise PermissionDenied
    if meeting.imported:
        raise PermissionDenied

    if not meeting.meetingtype.tops or not meeting.meetingtype.attachment_tops:
        raise Http404

    try:
        top = get_object_or_404(meeting.top_set, pk=top_pk)
    except ValidationError:
        raise Http404
    filename = top.attachment.path
    with open(filename, 'rb') as f:
        filetype = magic.from_buffer(f.read(1024), mime=True)
    with open(filename, 'rb') as f:
        wrapper = FileWrapper(f)
        response = HttpResponse(wrapper, content_type=filetype)

    return response


# add new top (allowed only by users with permission for the meetingtype or
# allowed for public if public-bit set)
def add(request: WSGIRequest, mt_pk: str, meeting_pk: UUID) -> HttpResponse:
    try:
        meeting = get_object_or_404(Meeting, pk=meeting_pk)
    except ValidationError:
        raise Http404
    if ((meeting.meetingtype.top_perms == "public" and not
            meeting.meetingtype.public) or
            meeting.meetingtype.top_perms == "perm"):
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        if not request.user.has_perm(meeting.meetingtype.permission()):
            raise PermissionDenied
    elif meeting.meetingtype.top_perms == "admin":
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or
                request.user == meeting.sitzungsleitung):
            raise PermissionDenied
    if meeting.imported:
        raise PermissionDenied

    if not meeting.meetingtype.tops:
        raise Http404

    if meeting.topdeadline_over and not request.user == \
            meeting.sitzungsleitung and not request.user.has_perm(
            meeting.meetingtype.admin_permission()):
        context = {'meeting': meeting,
                   'form': None}
        return render(request, 'tops/add.html', context)

    initial = {}
    authenticated = False
    if request.user.is_authenticated:
        initial['author'] = (request.user.first_name + " " +
                             request.user.last_name)
        initial['email'] = request.user.email
        authenticated = True

    if request.method == "POST":
        form = AddForm(request.POST, request.FILES, meeting=meeting,
                initial=initial, authenticated=authenticated)
        if form.is_valid():
            top = form.save()
            if (request.user.is_authenticated and
                    request.user.has_perm(meeting.meetingtype.permission())):
                top.user = request.user
                top.save()
            return redirect('viewmeeting', meeting.meetingtype.id, meeting.id)
    else:
        form = AddForm(meeting=meeting, initial=initial,
                authenticated=authenticated)

    context = {'meeting': meeting,
               'form': form}
    return render(request, 'tops/add.html', context)


# edit given top (allowed only by meetingtype-admin and sitzungsleitung)
@login_required
def edit(request: WSGIRequest, mt_pk: str, meeting_pk, top_pk) -> HttpResponse:
    try:
        meeting = get_object_or_404(Meeting, pk=meeting_pk)
    except ValidationError:
        raise Http404
    if not meeting.meetingtype.tops:
        raise Http404
    try:
        top = get_object_or_404(meeting.top_set, pk=top_pk)
    except ValidationError:
        raise Http404
    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung or
            (meeting.meetingtype.top_user_edit and not meeting.topdeadline_over
                and request.user.has_perm(meeting.meetingtype.permission())
                and request.user == top.user)):
        raise PermissionDenied
    elif meeting.imported:
        raise PermissionDenied

    user_edit = False
    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung):
        user_edit = True

    if request.method == "POST":
        form = EditForm(
            request.POST, request.FILES, instance=top, user_edit=user_edit,
        )
        if form.is_valid():
            form.save()
            return redirect('viewmeeting', meeting.meetingtype.id, meeting.id)
    else:
        form = EditForm(instance=top, user_edit=user_edit)

    context = {'meeting': meeting,
               'top': top,
               'form': form}
    return render(request, 'tops/edit.html', context)


# delete standard top (allowed only by meetingtype-admin and staff)
@login_required
def delete_std(request: WSGIRequest, mt_pk: str, top_pk) -> HttpResponse:
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    if not request.user.has_perm(meetingtype.admin_permission()) and not \
            request.user.is_staff:
        raise PermissionDenied

    if not meetingtype.tops or not meetingtype.standard_tops:
        raise Http404

    try:
        standardtop = get_object_or_404(meetingtype.standardtop_set, pk=top_pk)
    except ValidationError:
        raise Http404

    form = forms.Form(request.POST or None)
    if form.is_valid():
        meetingtype.standardtop_set.filter(pk=top_pk).delete()

        return redirect('liststdtops', meetingtype.id)

    context = {'meetingtype': meetingtype,
               'standardtop': standardtop,
               'form': form}
    return render(request, 'tops/del_std.html', context)


# add new standard top (allowed only by meetingtype-admin and staff)
@login_required
def add_std(request: WSGIRequest, mt_pk: str) -> HttpResponse:
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    if not request.user.has_perm(meetingtype.admin_permission()) and not \
            request.user.is_staff:
        raise PermissionDenied

    if not meetingtype.tops or not meetingtype.standard_tops:
        raise Http404

    form = AddStdForm(request.POST or None, meetingtype=meetingtype)
    if form.is_valid():
        form.save()

        return redirect('liststdtops', meetingtype.id)

    context = {'meetingtype': meetingtype,
               'form': form}
    return render(request, 'tops/add_std.html', context)


# edit standard top (allowed only by meetingtype-admin and staff)
@login_required
def edit_std(request: WSGIRequest, mt_pk: str, top_pk) -> HttpResponse:
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    if not request.user.has_perm(meetingtype.admin_permission()) and not \
            request.user.is_staff:
        raise PermissionDenied

    if not meetingtype.tops or not meetingtype.standard_tops:
        raise Http404

    try:
        standardtop = get_object_or_404(meetingtype.standardtop_set, pk=top_pk)
    except ValidationError:
        raise Http404

    form = EditStdForm(request.POST or None, instance=standardtop)
    if form.is_valid():
        form.save()

        return redirect('liststdtops', meetingtype.id)

    context = {'meetingtype': meetingtype,
               'standardtop': standardtop,
               'form': form}
    return render(request, 'tops/edit_std.html', context)


# list of standard tops (allowed only by meetingtype-admin or staff)
@login_required
def stdtops(request: WSGIRequest, mt_pk: str) -> HttpResponse:
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    if not request.user.has_perm(meetingtype.admin_permission()) and not \
            request.user.is_staff:
        raise PermissionDenied

    if not meetingtype.tops or not meetingtype.standard_tops:
        raise Http404

    standardtops = meetingtype.standardtop_set.order_by('topid')

    context = {'meetingtype': meetingtype,
               'standardtops': standardtops}
    return render(request, 'tops/list_std.html', context)


# sort standard tops (allowed only by meetingtype-admin or staff)
@login_required
def sort_stdtops(request: WSGIRequest, mt_pk: str) -> HttpResponse:
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    if not request.user.has_perm(meetingtype.admin_permission()) and not \
            request.user.is_staff:
        raise PermissionDenied

    if not meetingtype.tops or not meetingtype.standard_tops:
        raise Http404

    if request.method == "POST":
        tops = request.POST.getlist("tops[]", None)
        tops = [t for t in tops if t]
        if tops:
            for i, t in enumerate(tops):
                try:
                    pk = t.partition("_")[2]
                except IndexError:
                    return HttpResponseBadRequest('')
                try:
                    top = StandardTop.objects.get(pk=pk)
                except (StandardTop.DoesNotExist, ValidationError):
                    return HttpResponseBadRequest('')
                top.topid = i+1
                top.save()
            return JsonResponse({'success': True})

    return HttpResponseBadRequest('')
