from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse


from .models import Meeting

def index(request):
    # TODO
    meetings = Meeting.objects.order_by('time')

    context = {'meetings': meetings}
    return render(request, 'meetings/index.html', context)

def index_all(request):
    # TODO
    meetings = Meeting.objects.order_by('time')

    context = {'meetings': meetings}
    return render(request, 'meetings/index.html', context)

def view(request, mt_pk):
    # TODO
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    tops = meeting.top_set.order_by('topid')

    context = {'meeting': meeting,
               'tops': tops}
    return render(request, 'meetings/view.html', context)

def edit(request, mt_pk):
    # TODO
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    meeting.send_mail(request)

    return HttpResponseRedirect(reverse('viewmeeting', args=[meeting.id]))

