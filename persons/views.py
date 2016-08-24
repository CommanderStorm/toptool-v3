from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.forms import ValidationError
from django import forms
from django.utils import timezone
from django.core.exceptions import PermissionDenied

from toptool_common.shortcuts import render
from meetings.models import Meeting
from protokolle.models import Protokoll
from meetingtypes.models import MeetingType
from .forms import SelectPersonForm, EditAttendeeForm, AddPersonForm, \
    AddFunctionForm
from .models import Person, Attendee, Function


# list and create attendees for meeting (allowed only by meetingtype-admin,
# sitzungsleitung or protokollant)
@login_required
def add_attendees(request, mt_pk, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if meeting.protokollant:
        if not (request.user.has_perm(
                meeting.meetingtype.admin_permission()) or
                request.user == meeting.sitzungsleitung or
                request.user == meeting.protokollant):
            raise PermissionDenied
    else:
        if not request.user.has_perm(meeting.meetingtype.permission()):
            raise PermissionDenied

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
                return redirect('addattendees', meeting.meetingtype.id,
                    meeting.id)

            attendee = Attendee.objects.create(
                person=person,
                name=person.name,
                meeting=meeting,
                version=person.version,
            )

            attendee.person.last_created = timezone.now()
            attendee.person.save()

            for f in person.functions.iterator():
                attendee.functions.add(f)

            if not meeting.protokollant:
                meeting.protokollant = request.user
                meeting.save()

        return redirect('addattendees', meeting.meetingtype.id, meeting.id)

    context = {'meeting': meeting,
               'persons': persons,
               'attendees': attendees,
               'form': form}
    return render(request, 'persons/add_attendees.html', context)


# delete given attendee (allowed only by meetingtype-admin,
# sitzungsleitung or protokollant)
@login_required
def delete_attendee(request, mt_pk, meeting_pk, attendee_pk):
    attendee = get_object_or_404(Attendee, pk=attendee_pk)
    meeting = attendee.meeting
    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung or
            request.user == meeting.protokollant):
        raise PermissionDenied

    Attendee.objects.filter(pk=attendee_pk).delete()

    return redirect('addattendees', meeting.meetingtype.id, meeting.id)


# edit given attendee (allowed only by meetingtype-admin,
# sitzungsleitung or protokollant)
@login_required
def edit_attendee(request, mt_pk, meeting_pk, attendee_pk):
    attendee = get_object_or_404(Attendee, pk=attendee_pk)
    meeting = attendee.meeting
    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung or
            request.user == meeting.protokollant):
        raise PermissionDenied

    initial = {
        'functions': attendee.functions.all(),
    }

    form = EditAttendeeForm(request.POST or None, initial=initial,
            meetingtype=meeting.meetingtype)
    if form.is_valid():
        changePerson = False
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
            attendee.person.version = timezone.now()
            attendee.person.save()
            attendee.version = attendee.person.version
        if not changePerson:
            attendee.person = None
        attendee.save()

        return redirect('addattendees', meeting.meetingtype.id, meeting.id)

    context = {'attendee': attendee,
               'form': form}
    return render(request, 'persons/edit_attendee.html', context)


# add new person (allowed only by meetingtype-admin, sitzungsleitung or
# protokollant)
@login_required
def add_person(request, mt_pk, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not meeting.protokollant:
        if not request.user.has_perm(meeting.meetingtype.permission()):
            raise PermissionDenied
        meeting.protokollant = request.user
        meeting.save()
    elif not (request.user.has_perm(meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung or
            request.user == meeting.protokollant):
        raise PermissionDenied

    form = AddPersonForm(request.POST or None, meetingtype=meeting.meetingtype)
    if form.is_valid():
        form.save()

        return redirect('addattendees', meeting.meetingtype.id, meeting.id)

    context = {'meeting': meeting,
               'form': form}
    return render(request, 'persons/add_person.html', context)


# select persons to delete (allowed only by meetingtype-admin or staff)
@login_required
def delete_persons(request, mt_pk):
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    if not request.user.has_perm(meetingtype.admin_permission()) and not \
            request.user.is_staff:
        raise PermissionDenied

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
                return redirect('delperson', meetingtype.id, person.id)
        return redirect('delpersons', meetingtype.id)

    context = {'meetingtype': meetingtype,
               'persons': persons,
               'form': form}
    return render(request, 'persons/del_persons.html', context)


# delete person (allowed only by meetingtype-admin or staff)
@login_required
def delete_person(request, mt_pk, person_pk):
    person = get_object_or_404(Person, pk=person_pk)
    meetingtype = person.meetingtype
    if not (request.user.has_perm(meetingtype.admin_permission()) or
            request.user.is_staff):
        raise PermissionDenied

    form = forms.Form(request.POST or None)
    if form.is_valid():
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
        raise PermissionDenied

    functions = Function.objects.filter(meetingtype=meetingtype).order_by(
        'sort_name', 'name')

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
def delete_function(request, mt_pk, function_pk):
    function = get_object_or_404(Function, pk=function_pk)
    meetingtype = function.meetingtype
    if not request.user.has_perm(meetingtype.admin_permission()) and not \
            request.user.is_staff:
        raise PermissionDenied

    Function.objects.filter(pk=function_pk).delete()

    return redirect('functions', meetingtype.id)
