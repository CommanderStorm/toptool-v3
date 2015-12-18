from django.shortcuts import render

from .models import Meeting

def index(request):
    meetings = Meeting.objects.order_by('time')

    context = {'meetings': meetings}
    return render(request, 'meetings/index.html', context)

