from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django import forms

from meetings.models import Meeting
from .forms import AddForm, EditForm
from toptool_common.shortcuts import render


# list of tops for a meeting (allowed only by users with permission for the
# meetingtype or allowed for public if public-bit set)
# this is only used to embed the tops in the homepage
def list(request, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not meeting.meetingtype.public: # public access disabled
        if not request.user.is_authenticated():
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        if not request.user.has_perm(meeting.meetingtype.permission()):
            raise Http404("Access Denied")

    tops = meeting.top_set.order_by('topid')

    context = {'meeting': meeting,
               'tops': tops}
    return render(request, 'tops/view.html', context)


# delete given (allowed only by meetingtype-admin and sitzungsleitung)
@login_required
def delete(request, meeting_pk, topid):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not request.user.has_perm(meeting.meetingtype.admin_permission()) and not \
            request.user == meeting.sitzungsleitung:
        raise Http404("Access Denied")

    top = get_object_or_404(meeting.top_set, topid=topid)
    
    form = forms.Form(request.POST or None)
    if form.is_valid():
        meeting.top_set.filter(topid=topid).delete()

        return HttpResponseRedirect(reverse('viewmeeting', args=[meeting.id]))

    context = {'meeting': meeting,
               'top': top,
               'form': form}
    return render(request, 'tops/del.html', context)


# add new top (allowed only by users with permission for the meetingtype or
# allowed for public if public-bit set)
def add(request, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not meeting.meetingtype.public: # public access disabled
        if not request.user.is_authenticated():
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        if not request.user.has_perm(meeting.meetingtype.permission()):
            raise Http404("Access Denied")

    form = AddForm(request.POST or None, meeting=meeting)
    if form.is_valid():
        form.save()

        return HttpResponseRedirect(reverse('viewmeeting', args=[meeting.id]))

    context = {'meeting': meeting,
               'form': form}
    return render(request, 'tops/add.html', context)


# edit given top (allowed only by meetingtype-admin and sitzungsleitung)
@login_required
def edit(request, meeting_pk, topid):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not request.user.has_perm(meeting.meetingtype.admin_permission()) and not \
            request.user == meeting.sitzungsleitung:
        raise Http404("Access Denied")

    top = get_object_or_404(meeting.top_set, topid=topid)

    initial = {
        'title': top.title,
        'author': top.author,
        'email': top.email,
        'description': top.description,
        'protokoll_templ': top.protokoll_templ,
    }

    form = EditForm(request.POST or None, initial=initial)
    if form.is_valid():
        meeting.top_set.filter(topid=topid).update(
            title=form.cleaned_data['title'],
            author=form.cleaned_data['author'],
            description=form.cleaned_data['description'],
            protokoll_templ=form.cleaned_data['protokoll_templ'],
        )

        return HttpResponseRedirect(reverse('viewmeeting', args=[meeting.id]))

    context = {'meeting': meeting,
               'top': top,
               'form': form}
    return render(request, 'tops/edit.html', context)


