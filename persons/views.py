from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.forms import ValidationError
from django import forms

from toptool_common.shortcuts import render
from meetings.models import Meeting
from meetingtypes.models import MeetingType
from .forms import SelectPersonForm, EditAttendeeForm, AddPersonForm, \
    AddFunctionForm
from .models import Person, Attendee, Function

# list and create attendees for meeting (allowed only by meetingtype-admin,
# sitzungsleitung or protokollant)
@login_required
def add_attendees(request, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung or
            request.user == meeting.protokollant):
        return render(request, 'toptool_common/access_denied.html', {})

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
        return render(request, 'toptool_common/access_denied.html', {})

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
        return render(request, 'toptool_common/access_denied.html', {})

    initial = {
        'functions': attendee.functions.all(),
    }

    form = EditAttendeeForm(request.POST or None, initial=initial)
    if form.is_valid():
        if attendee.person and attendee.version == attendee.person.version:
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
        if not changePerson:
            attendee.name_=attendee.person.name
            attendee.person=None
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
        return render(request, 'toptool_common/access_denied.html', {})

    form = AddPersonForm(request.POST or None, meetingtype=meeting.meetingtype)
    if form.is_valid():
        form.save()
        
        return redirect('addattendees', meeting.id)

    context = {'meeting': meeting,
               'form': form}
    return render(request, 'persons/add_person.html', context)


# select persons to delete (allowed only by meetingtype-admin or staff)
@login_required
def delete_persons(request, mt_pk):
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    if not request.user.has_perm(meetingtype.admin_permission()) and not \
            request.user.is_staff:
        return render(request, 'toptool_common/access_denied.html', {})

    persons = Person.objects.filter(meetingtype=meetingtype).order_by('name')

    form = SelectPersonForm(request.POST or None)
    if form.is_valid():
        person_id = form.cleaned_data['person']
        if person_id:
            try:
                person = persons.get(id=person_id)
            except Person.DoesNotExist:
                return redirect('delpersons', meetingtype.id)
            else:
                return redirect('delperson', person.id)
        return redirect('delpersons', meetingtype.id)

    context = {'meetingtype': meetingtype,
               'persons': persons,
               'form': form}
    return render(request, 'persons/del_persons.html', context)


# delete person (allowed only by meetingtype-admin or staff)
@login_required
def delete_person(request, person_pk):
    person = get_object_or_404(Person, pk=person_pk)
    meetingtype=person.meetingtype
    if not (request.user.has_perm(meetingtype.admin_permission()) or
            request.user.is_staff):
        return render(request, 'toptool_common/access_denied.html', {})


    form = forms.Form(request.POST or None)
    if form.is_valid():
        attendees = person.attendee_set

        for a in attendees.iterator():
            a.name_ = a.person.name
            a.person = None
            a.save()

        Person.objects.filter(pk=person_pk).delete()

        return redirect('delpersons', meetingtype.id)

    context = {'person': person,
               'form': form}
    return render(request, 'persons/del_person.html', context)


# add or remove functions (allowed only by meetingtype-admin or staff)
@login_required
def functions(request, mt_pk):
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    if not request.user.has_perm(meetingtype.admin_permission()) and not \
            request.user.is_staff:
        return render(request, 'toptool_common/access_denied.html', {})

    functions = Function.objects.filter(meetingtype=meetingtype).order_by('name')

    form = AddFunctionForm(request.POST or None, meetingtype=meetingtype)
    if form.is_valid():
        form.save()

        return redirect('functions', meetingtype.id)

    context = {'meetingtype': meetingtype,
               'functions': functions,
               'form': form}
    return render(request, 'persons/functions.html', context)


# delete function (allowed only by meetingtype-admin or staff)
@login_required
def delete_function(request, function_pk):
    function = get_object_or_404(Function, pk=function_pk)
    meetingtype = function.meetingtype
    if not request.user.has_perm(meetingtype.admin_permission()) and not \
            request.user.is_staff:
        return render(request, 'toptool_common/access_denied.html', {})

    Function.objects.filter(pk=function_pk).delete()
    
    return redirect('functions', meetingtype.id)


