from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.http import Http404

from .models import MeetingType
from meetings.models import Meeting
from .forms import MTAddForm, MeetingAddForm

# select a meeting type (lists only meeting types the user is a member of)
@login_required
def index(request):
    meetingtypes = MeetingType.objects.order_by('name')

    context = {'meetingtypes': meetingtypes}
    return render(request, 'meetingtypes/index.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def index_all(request):
    meetingtypes = MeetingType.objects.order_by('name')

    context = {'meetingtypes': meetingtypes}
    return render(request, 'meetingtypes/index_all.html', context)

@login_required
def view(request, mt_pk):
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    if not request.user.has_perm(meetingtype.permission):
        raise Http404("Access Denied")

    meetings = meetingtype.meeting_set.order_by('time')

    context = {'meetingtype': meetingtype,
               'meetings': meetings}
    return render(request, 'meetingtypes/view.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def add(request):
    form = MTForm(request.POST or None)
    if form.is_valid():
        content_type = ContentType.objects.get_for_model(MeetingType)
        
        name=form.cleaned_data['name']
        shortname=form.cleaned_data['shortname']
        group=form.cleaned_data['group']
        admin_group=form.cleaned_data['admin_group']
        admin_users=form.cleaned_data['admin_users']

        app_name =  request.resolver_match.app_name

        permission = Permission.objects.create(codename=shortname,
            name="permission for " + name, content_type=content_type)
        perm = app_name + "." + permission.codename

        admin_permission = Permission.objects.create(
            codename=shortname+"_admin",
            name="admin_permission for " + name,
            content_type=content_type)
        admin_perm = app_name + "." + admin_permission.codename

        group.permissions.add(permission)
        if admin_group:
            admin_group.permissions.add(permission)
            admin_group.permissions.add(admin_permission)
        for u in admin_users:
            u.user_permissions.add(permission)
            u.user_permissions.add(admin_permission)

        MeetingType.objects.create(
            name=name,
            shortname=shortname,
            permission=perm,
            admin_permission=admin_perm,
            mailinglist=form.cleaned_data['mailinglist'],
            approve=form.cleaned_data['approve'],
            attendance=form.cleaned_data['attendance'],
        )

        return redirect('allmts')

    context = {'form': form}
    return render(request, 'meetingtypes/add.html', context)

@login_required
def edit(request, mt_pk):
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    if not request.user.has_perm(meetingtype.admin_permission):
        raise Http404("Access Denied")
    # TODO


@login_required
def add_meeting(request, mt_pk):
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    if not request.user.has_perm(meetingtype.admin_permission):
        raise Http404("Access Denied")

    form = MeetingAddForm(request.POST or None, meetingtype=meetingtype)
    if form.is_valid():
        form.save()

        return HttpResponseRedirect(reverse('viewmt', args=[meetingtype.id]))

    context = {'meetingtype': meetingtype,
               'form': form}
    return render(request, 'meetingtypes/add_meeting.html', context)


