from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from .models import MeetingType
from meetings.models import Meeting

def index(request):
    meetingtypes = MeetingType.objects.order_by('name')

    context = {'meetingtypes': meetingtypes}
    return render(request, 'meetingtypes/index.html', context)

def index_all(request):
    meetingtypes = MeetingType.objects.order_by('name')

    context = {'meetingtypes': meetingtypes}
    return render(request, 'meetingtypes/index_all.html', context)

def view(request, mt_pk):
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    meetings = meetingtype.meeting_set.order_by('time')

    context = {'meetingtype': meetingtype,
               'meetings': meetings}
    return render(request, 'meetingtypes/view.html', context)

def edit(request, mt_pk):
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    # TODO

