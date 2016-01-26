from django.shortcuts import render, get_object_or_404


from .models import Meeting

def index(request):
    meetings = Meeting.objects.order_by('time')

    context = {'meetings': meetings}
    return render(request, 'meetings/index.html', context)


def view(request, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    tops = meeting.top_set.order_by('topid')

    context = {'meeting': meeting,
               'tops': tops}
    return render(request, 'meetings/view.html', context)

