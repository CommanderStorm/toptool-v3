from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from meetings.models import Meeting
from .forms import DelForm, AddForm


def view(request, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    tops = meeting.top_set.order_by('topid')

    context = {'meeting': meeting,
               'tops': tops}
    return render(request, 'tops/view.html', context)


def delete(request, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    tops = meeting.top_set.order_by('topid')

    # response form
    # the "request.POST or None" shortens the view. otherwise one would have
    # to check if request.POST is not none and initializie the form then
    form = DelForm(request.POST or None, tops=tops)
    if form.is_valid():
        del_top = form.cleaned_data['top']
        meeting.top_set.filter(topid=del_top).delete()

        return HttpResponseRedirect(reverse('view', args=[meeting.id]))

    context = {'meeting': meeting,
               'form': form}
    return render(request, 'tops/del.html', context)


def add(request, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)

    # response form
    # the "request.POST or None" shortens the view. otherwise one would have
    # to check if request.POST is not none and initializie the form then
    form = AddForm(request.POST or None, meeting=meeting)
    if form.is_valid():
        form.save()

        return HttpResponseRedirect(reverse('view', args=[meeting.id]))

    context = {'meeting': meeting,
               'form': form}
    return render(request, 'tops/add.html', context)


