from wsgiref.util import FileWrapper

from django.shortcuts import get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.views.decorators.clickjacking import xframe_options_exempt
from django.http import HttpResponseBadRequest, HttpResponse, Http404
from django.http.response import JsonResponse

from meetings.models import Meeting
from meetingtypes.models import MeetingType
from .forms import AddForm, EditForm, AddStdForm, EditStdForm
from .models import Top, StandardTop
from toptool.shortcuts import render


# edit list of tops (allowed only by meetingtype-admin and sitzungsleitung)
@login_required
def tops(request, mt_pk, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung):
        raise PermissionDenied
    if meeting.imported:
        raise PermissionDenied

    tops = meeting.get_tops_with_id()

    context = {
        'meeting': meeting,
        'tops': tops,
    }
    return render(request, 'tops/list.html', context)


# sort tops (allowed only by meetingtype-admin and sitzungsleitung)
@login_required
def sort_tops(request, mt_pk, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung):
        raise PermissionDenied
    if meeting.imported:
        raise PermissionDenied

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
def list(request, mt_pk, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not meeting.meetingtype.public:          # public access disabled
        if not request.user.is_authenticated():
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        if not request.user.has_perm(meeting.meetingtype.permission()):
            raise PermissionDenied
    if meeting.imported:
        raise PermissionDenied

    tops = meeting.get_tops_with_id()

    context = {'meeting': meeting,
               'tops': tops}
    return render(request, 'tops/view.html', context)


# show that there exists no next meeting
@xframe_options_exempt
def nonext(request, mt_pk):
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    if not meetingtype.public:          # public access disabled
        if not request.user.is_authenticated():
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        if not request.user.has_perm(meetingtype.permission()):
            raise PermissionDenied

    context = {'meetingtype': meetingtype}
    return render(request, 'tops/nonext.html', context)


# delete given top (allowed only by meetingtype-admin and sitzungsleitung)
@login_required
def delete(request, mt_pk, meeting_pk, top_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung):
        raise PermissionDenied
    if meeting.imported:
        raise PermissionDenied

    top = get_object_or_404(meeting.top_set, pk=top_pk)

    form = forms.Form(request.POST or None)
    if form.is_valid():
        meeting.top_set.filter(pk=top_pk).delete()

        return redirect('viewmeeting', meeting.meetingtype.id, meeting.id)

    context = {'meeting': meeting,
               'top': top,
               'form': form}
    return render(request, 'tops/del.html', context)


# show top attachment (allowed only by users with permission for the
# meetingtype)
@login_required
def show_attachment(request, mt_pk, meeting_pk, top_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not request.user.has_perm(meeting.meetingtype.permission()):
        raise PermissionDenied
    if meeting.imported:
        raise PermissionDenied

    if not meeting.meetingtype.attachment_tops:
        raise Http404

    top = get_object_or_404(meeting.top_set, pk=top_pk)
    filename = top.attachment.path
    wrapper = FileWrapper(open(filename, 'rb'))
    response = HttpResponse(wrapper, content_type='application/pdf')

    return response


# add new top (allowed only by users with permission for the meetingtype or
# allowed for public if public-bit set)
def add(request, mt_pk, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if ((meeting.meetingtype.top_perms == "public" and not
            meeting.meetingtype.public) or
            meeting.meetingtype.top_perms == "perm"):
        if not request.user.is_authenticated():
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        if not request.user.has_perm(meeting.meetingtype.permission()):
            raise PermissionDenied
    elif meeting.meetingtype.top_perms == "admin":
        if not request.user.is_authenticated():
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or
                request.user == meeting.sitzungsleitung):
            raise PermissionDenied
    if meeting.imported:
        raise PermissionDenied

    if meeting.topdeadline_over and not request.user == \
            meeting.sitzungsleitung and not request.user.has_perm(
            meeting.meetingtype.admin_permission()):
        context = {'meeting': meeting,
                   'form': None}
        return render(request, 'tops/add.html', context)

    initial = {}
    authenticated = False
    if request.user.is_authenticated():
        initial['author'] = (request.user.first_name + " " +
                             request.user.last_name)
        initial['email'] = request.user.email
        authenticated = True

    if request.method == "POST":
        form = AddForm(request.POST, request.FILES, meeting=meeting,
                initial=initial, authenticated=authenticated)
        if form.is_valid():
            form.save()
            return redirect('viewmeeting', meeting.meetingtype.id, meeting.id)
    else:
        form = AddForm(meeting=meeting, initial=initial,
                authenticated=authenticated)

    context = {'meeting': meeting,
               'form': form}
    return render(request, 'tops/add.html', context)


# edit given top (allowed only by meetingtype-admin and sitzungsleitung)
@login_required
def edit(request, mt_pk, meeting_pk, top_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung):
        raise PermissionDenied
    elif meeting.imported:
        raise PermissionDenied

    top = get_object_or_404(meeting.top_set, pk=top_pk)

    if request.method == "POST":
        form = EditForm(request.POST, request.FILES, instance=top)
        if form.is_valid():
            form.save()
            return redirect('viewmeeting', meeting.meetingtype.id, meeting.id)
    else:
        form = EditForm(instance=top)

    context = {'meeting': meeting,
               'top': top,
               'form': form}
    return render(request, 'tops/edit.html', context)


# delete standard top (allowed only by meetingtype-admin and staff)
@login_required
def delete_std(request, mt_pk, top_pk):
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    if not request.user.has_perm(meetingtype.admin_permission()) and not \
            request.user.is_staff:
        raise PermissionDenied

    if not meetingtype.standard_tops:
        raise Http404

    standardtop = get_object_or_404(meetingtype.standardtop_set, pk=top_pk)

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
def add_std(request, mt_pk):
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    if not request.user.has_perm(meetingtype.admin_permission()) and not \
            request.user.is_staff:
        raise PermissionDenied

    if not meetingtype.standard_tops:
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
def edit_std(request, mt_pk, top_pk):
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    if not request.user.has_perm(meetingtype.admin_permission()) and not \
            request.user.is_staff:
        raise PermissionDenied

    if not meetingtype.standard_tops:
        raise Http404

    standardtop = get_object_or_404(meetingtype.standardtop_set, pk=top_pk)

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
def stdtops(request, mt_pk):
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    if not request.user.has_perm(meetingtype.admin_permission()) and not \
            request.user.is_staff:
        raise PermissionDenied

    if not meetingtype.standard_tops:
        raise Http404

    standardtops = meetingtype.standardtop_set.order_by('topid')

    context = {'meetingtype': meetingtype,
               'standardtops': standardtops}
    return render(request, 'tops/list_std.html', context)


# sort standard tops (allowed only by meetingtype-admin or staff)
@login_required
def sort_stdtops(request, mt_pk):
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    if not request.user.has_perm(meetingtype.admin_permission()) and not \
            request.user.is_staff:
        raise PermissionDenied

    if not meetingtype.standard_tops:
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
