from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.forms import ValidationError

from toptool_common.shortcuts import render
from meetings.models import Meeting
from .forms import SelectPersonForm, EditAttendeeForm, AddPersonForm
from .models import Person, Attendee

# list and create attendees for meeting (allowed only by meetingtype-admin,
# sitzungsleitung or protokollant)
@login_required
def add_attendees(request, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung or
            request.user == meeting.protokollant):
        raise Http404("Access Denied")

    attendees = meeting.attendee_set.order_by('person__name')
    selected_persons = attendees.values('person')
    persons = Person.objects.filter(meetingtype=meeting.meetingtype).exclude(
        id__in=selected_persons).order_by('name')

    form = SelectPersonForm(request.POST or None)
    if form.is_valid():
        person_id = form.cleaned_data['person']
        if person_id:
            try:
                person = persons.get(id=person_id)
            except Person.DoesNotExist:
                return redirect('addattendees', meeting.id)
                

            attendee = Attendee.objects.create(
                person=person,
                meeting=meeting,
                version=person.version,
            )

            for f in person.functions.iterator():
                attendee.functions.add(f)

        return redirect('addattendees', meeting.id)

    context = {'meeting': meeting,
               'persons': persons,
               'attendees': attendees,
               'form': form}
    return render(request, 'persons/add_attendees.html', context)


# delete given attendee (allowed only by meetingtype-admin,
# sitzungsleitung or protokollant)
@login_required
def delete_attendee(request, attendee_pk):
    attendee = get_object_or_404(Attendee, pk=attendee_pk)
    meeting = attendee.meeting
    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung or
            request.user == meeting.protokollant):
        raise Http404("Access Denied")

    Attendee.objects.filter(pk=attendee_pk).delete()

    return redirect('addattendees', meeting.id)


# edit given attendee (allowed only by meetingtype-admin,
# sitzungsleitung or protokollant)
@login_required
def edit_attendee(request, attendee_pk):
    attendee = get_object_or_404(Attendee, pk=attendee_pk)
    meeting = attendee.meeting
    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung or
            request.user == meeting.protokollant):
        raise Http404("Access Denied")

    initial = {
        'functions': attendee.functions.all(),
    }

    form = EditAttendeeForm(request.POST or None, initial=initial)
    if form.is_valid():
        if attendee.version == attendee.person.version:
            changePerson = True
        attendee.functions.clear()
        if changePerson:
            attendee.person.functions.clear()
        for f in form.cleaned_data['functions'].iterator():
            attendee.functions.add(f)
            if changePerson:
                attendee.person.functions.add(f)
        if changePerson:
            attendee.version=attendee.person.version
            attendee.save()
        
        return redirect('addattendees', meeting.id)

    context = {'attendee': attendee,
               'form': form}
    return render(request, 'persons/edit_attendee.html', context)


# add new person (allowed only by meetingtype-admin, sitzungsleitung or
# protokollant)
@login_required
def add_person(request, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung or
            request.user == meeting.protokollant):
        raise Http404("Access Denied")

    form = AddPersonForm(request.POST or None, meetingtype=meeting.meetingtype)
    if form.is_valid():
        form.save()
        
        return redirect('addattendees', meeting.id)

    context = {'meeting': meeting,
               'form': form}
    return render(request, 'persons/add_person.html', context)

