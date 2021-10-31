from urllib.parse import urlencode
from uuid import UUID

from django import forms
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseBadRequest
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone

from meetings.models import Meeting
from meetingtypes.models import MeetingType
from toptool.utils.helpers import get_meeting_or_404_on_validation_error
from toptool.utils.permission import (
    is_admin_sitzungsleitung_protokoll_minute_takers,
    is_admin_staff,
    require,
)
from toptool.utils.shortcuts import render
from toptool.utils.typing import AuthWSGIRequest

from .forms import (
    AddFunctionForm,
    AddPersonForm,
    EditAttendeeForm,
    EditFunctionForm,
    SelectPersonForm,
)
from .models import Attendee, Function, Person


# list and create attendees for meeting (allowed only by meetingtype-admin,
# sitzungsleitung or protokollant)
@login_required
def add_attendees(
    request: AuthWSGIRequest,
    mt_pk: str,
    meeting_pk: UUID,
) -> HttpResponse:
    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)
    if not (
        request.user.has_perm(meeting.meetingtype.admin_permission())
        or request.user == meeting.sitzungsleitung
        or (
            meeting.meetingtype.protokoll
            and request.user in meeting.minute_takers.all()
        )
    ):
        raise PermissionDenied
    if meeting.imported:
        raise PermissionDenied
    if not meeting.meetingtype.attendance:
        raise Http404

    attendees = meeting.attendee_set.order_by("person__name")
    selected_persons = attendees.values("person")
    persons = (
        Person.objects.filter(meetingtype=meeting.meetingtype)
        .exclude(id__in=selected_persons)
        .order_by("name")
    )

    form = SelectPersonForm(request.POST or None, persons=persons)
    if form.is_valid():
        if "addperson" in request.POST:
            label = form.cleaned_data["person_label"]
            if label:
                url = reverse(
                    "addperson",
                    args=[meeting.meetingtype.id, meeting.id],
                )
                encoded_label = urlencode({"name": label})
                return redirect(f"{url}?{encoded_label}")
            return redirect("addperson", meeting.meetingtype.id, meeting.id)
        else:
            person = form.cleaned_data["person"]
            if person:
                attendee = Attendee.objects.create(
                    person=person,
                    name=person.name,
                    meeting=meeting,
                    version=person.version,
                )
                if attendee.person:  # required for mypy. in reality unnecessary
                    attendee.person.last_selected = timezone.now()
                    attendee.person.save()

                for function in person.functions.iterator():
                    attendee.functions.add(function)

            return redirect("addattendees", meeting.meetingtype.id, meeting.id)

    context = {
        "meeting": meeting,
        "functions": meeting.meetingtype.function_set.exists(),
        "persons": persons,
        "attendees": attendees,
        "form": form,
    }
    return render(request, "persons/add_attendees.html", context)


# delete given attendee (allowed only by meetingtype-admin,
# sitzungsleitung or protokollant)
@login_required
def delete_attendee(
    request: AuthWSGIRequest,
    mt_pk: str,
    meeting_pk: UUID,
    attendee_pk: int,
) -> HttpResponse:
    attendee = get_object_or_404(Attendee, pk=attendee_pk)
    meeting = attendee.meeting

    require(is_admin_sitzungsleitung_protokoll_minute_takers(request, meeting))
    if meeting.imported:
        raise PermissionDenied

    if not meeting.meetingtype.attendance:
        raise Http404

    Attendee.objects.filter(pk=attendee_pk).delete()

    return redirect("addattendees", meeting.meetingtype.id, meeting.id)


# edit given attendee (allowed only by meetingtype-admin,
# sitzungsleitung or protokollant)
@login_required
def edit_attendee(
    request: AuthWSGIRequest,
    mt_pk: str,
    meeting_pk: UUID,
    attendee_pk: int,
) -> HttpResponse:
    attendee = get_object_or_404(Attendee, pk=attendee_pk)
    meeting: Meeting = attendee.meeting
    require(is_admin_sitzungsleitung_protokoll_minute_takers(request, meeting))
    if meeting.imported:
        raise PermissionDenied

    if (
        not meeting.meetingtype.attendance
        or not meeting.meetingtype.attendance_with_func
        or not meeting.meetingtype.function_set.exists()
    ):
        raise Http404

    initial = {
        "functions": attendee.functions.all(),
    }

    form = EditAttendeeForm(
        request.POST or None,
        initial=initial,
        meetingtype=meeting.meetingtype,
    )
    if form.is_valid():
        change_person = attendee.person and attendee.version == attendee.person.version
        attendee.functions.clear()
        if change_person and attendee.person:
            attendee.person.functions.clear()
        for function in form.cleaned_data["functions"].iterator():
            attendee.functions.add(function)
            if change_person and attendee.person:
                attendee.person.functions.add(function)
        if change_person and attendee.person:
            attendee.person.version = timezone.now()
            attendee.person.save()
            attendee.version = attendee.person.version
        if not change_person:
            attendee.person = None
        attendee.save()

        return redirect("addattendees", meeting.meetingtype.id, meeting.id)

    context = {
        "attendee": attendee,
        "form": form,
    }
    return render(request, "persons/edit_attendee.html", context)


# add new person (allowed only by meetingtype-admin, sitzungsleitung or
# protokollant)
@login_required
def add_person(request: AuthWSGIRequest, mt_pk: str, meeting_pk: UUID) -> HttpResponse:
    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)
    require(is_admin_sitzungsleitung_protokoll_minute_takers(request, meeting))
    if meeting.imported:
        raise PermissionDenied

    if not meeting.meetingtype.attendance:
        raise Http404

    initial = {}
    name = request.GET.get("name", None)
    if name:
        initial = {"name": name}
    form = AddPersonForm(
        request.POST or None,
        meetingtype=meeting.meetingtype,
        initial=initial,
    )
    if form.is_valid():
        person = form.save()
        attendee = Attendee.objects.create(
            person=person,
            name=person.name,
            meeting=meeting,
            version=person.version,
        )
        if not attendee.person:
            raise Http404("cannot happen, but mypy does think it can")
        attendee.person.last_selected = timezone.now()
        attendee.person.save()

        for function in person.functions.iterator():
            attendee.functions.add(function)

        return redirect("addattendees", meeting.meetingtype.id, meeting.id)

    context = {
        "meeting": meeting,
        "form": form,
    }
    return render(request, "persons/add_person.html", context)


# list all persons of a meetingtype (allowed only by meetingtype-admin or staff)
@login_required
def list_persons(request: AuthWSGIRequest, mt_pk: str) -> HttpResponse:
    meetingtype: MeetingType = get_object_or_404(MeetingType, pk=mt_pk)
    if (
        not request.user.has_perm(meetingtype.admin_permission())
        and not request.user.is_staff
    ):
        raise PermissionDenied

    if not meetingtype.attendance:
        raise Http404

    persons = Person.objects.filter(meetingtype=meetingtype).order_by("name")

    if request.method == "POST":
        if "addperson" in request.POST:
            form = SelectPersonForm(request.POST or None, persons=persons)
            if form.is_valid():
                label = form.cleaned_data["person_label"]
                if label:
                    url = reverse("addplainperson", args=[meetingtype.id])
                    encoded_label = urlencode({"name": label})
                    return redirect(f"{url}?{encoded_label}")
                else:
                    return redirect("addplainperson", meetingtype.id)

        else:
            form = SelectPersonForm(request.POST or None, persons=persons)
            if form.is_valid():
                person = form.cleaned_data["person"]
                if person:
                    return redirect("editperson", meetingtype.id, person.id)
                return redirect("persons", meetingtype.id)
    else:
        form = SelectPersonForm(persons=persons)

    context = {
        "meetingtype": meetingtype,
        "persons": persons,
        "form": form,
    }
    return render(request, "persons/persons.html", context)


# add new person for meetingtype (allowed only by meetingtype-admin or staff)
@login_required
def add_plain_person(request: AuthWSGIRequest, mt_pk: str) -> HttpResponse:
    meetingtype: MeetingType = get_object_or_404(MeetingType, pk=mt_pk)
    if (
        not request.user.has_perm(meetingtype.admin_permission())
        and not request.user.is_staff
    ):
        raise PermissionDenied

    if not meetingtype.attendance:
        raise Http404

    initial = {}
    name = request.GET.get("name", None)
    if name:
        initial = {"name": name}
    form = AddPersonForm(
        request.POST or None,
        meetingtype=meetingtype,
        initial=initial,
    )
    if form.is_valid():
        form.save()

        return redirect("persons", meetingtype.id)

    context = {
        "meetingtype": meetingtype,
        "form": form,
    }
    return render(request, "persons/add_plain_person.html", context)


# edit person (allowed only by meetingtype-admin or staff)
@login_required
def edit_person(request: AuthWSGIRequest, mt_pk: str, person_pk: int) -> HttpResponse:
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    require(is_admin_staff(request, meetingtype))

    if not meetingtype.attendance:
        raise Http404

    person: Person = get_object_or_404(meetingtype.person_set, pk=person_pk)

    form = AddPersonForm(
        request.POST or None,
        meetingtype=meetingtype,
        instance=person,
    )
    if form.is_valid():
        person = form.save()
        person.version = timezone.now()
        person.save()

        return redirect("persons", meetingtype.id)

    context = {
        "meetingtype": meetingtype,
        "person": person,
        "form": form,
    }
    return render(request, "persons/edit_person.html", context)


# delete person (allowed only by meetingtype-admin or staff)
@login_required
def delete_person(request: AuthWSGIRequest, mt_pk: str, person_pk: int) -> HttpResponse:
    person = get_object_or_404(Person, pk=person_pk)
    meetingtype = person.meetingtype
    if not (
        request.user.has_perm(meetingtype.admin_permission()) or request.user.is_staff
    ):
        raise PermissionDenied

    if not meetingtype.attendance:
        raise Http404

    form = forms.Form(request.POST or None)
    if form.is_valid():
        Person.objects.filter(pk=person_pk).delete()

        return redirect("persons", meetingtype.id)

    context = {
        "meetingtype": meetingtype,
        "person": person,
        "form": form,
    }
    return render(request, "persons/del_person.html", context)


# add or remove functions (allowed only by meetingtype-admin or staff)
@login_required
def manage_functions(request: AuthWSGIRequest, mt_pk: str) -> HttpResponse:
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    if (
        not request.user.has_perm(meetingtype.admin_permission())
        and not request.user.is_staff
    ):
        raise PermissionDenied

    if not meetingtype.attendance or not meetingtype.attendance_with_func:
        raise Http404

    functions = Function.objects.filter(meetingtype=meetingtype).order_by(
        "sort_order",
        "name",
    )

    form = AddFunctionForm(request.POST or None, meetingtype=meetingtype)
    if form.is_valid():
        form.save()

        return redirect("functions", meetingtype.id)

    context = {
        "meetingtype": meetingtype,
        "functions": functions,
        "form": form,
    }
    return render(request, "persons/functions.html", context)


# sort functions (allowed only by meetingtype-admin or staff)
@login_required
def sort_functions(request: AuthWSGIRequest, mt_pk: str) -> HttpResponse:
    meetingtype: MeetingType = get_object_or_404(MeetingType, pk=mt_pk)
    if (
        not request.user.has_perm(meetingtype.admin_permission())
        and not request.user.is_staff
    ):
        raise PermissionDenied

    if not meetingtype.attendance or not meetingtype.attendance_with_func:
        raise Http404

    if request.method == "POST":
        functions = request.POST.getlist("functions[]", None)
        if functions:
            for counter, function in enumerate(functions):
                try:
                    function_pk = int(function.partition("_")[2])
                except (ValueError, IndexError):
                    return HttpResponseBadRequest("")
                try:
                    func = Function.objects.get(pk=function_pk)
                except Function.DoesNotExist:
                    return HttpResponseBadRequest("")
                func.sort_order = counter
                func.save()
            return JsonResponse({"success": True})

    return HttpResponseBadRequest("")


# edit function (allowed only by meetingtype-admin or staff)
@login_required
def edit_function(
    request: AuthWSGIRequest,
    mt_pk: str,
    function_pk: int,
) -> HttpResponse:
    function = get_object_or_404(Function, pk=function_pk)
    meetingtype = function.meetingtype
    if (
        not request.user.has_perm(meetingtype.admin_permission())
        and not request.user.is_staff
    ):
        raise PermissionDenied

    if not meetingtype.attendance or not meetingtype.attendance_with_func:
        raise Http404

    form = EditFunctionForm(request.POST or None, instance=function)
    if form.is_valid():
        form.save()

        return redirect("functions", meetingtype.id)

    context = {
        "meetingtype": meetingtype,
        "function": function,
        "form": form,
    }
    return render(request, "persons/edit_function.html", context)


@login_required
def delete_function(
    request: AuthWSGIRequest,
    mt_pk: str,
    function_pk: int,
) -> HttpResponse:
    function = get_object_or_404(Function, pk=function_pk)
    meetingtype = function.meetingtype
    if (
        not request.user.has_perm(meetingtype.admin_permission())
        and not request.user.is_staff
    ):
        raise PermissionDenied

    if not meetingtype.attendance or not meetingtype.attendance_with_func:
        raise Http404

    form = forms.Form(request.POST or None)
    if form.is_valid():
        function.delete()

        return redirect("functions", meetingtype.id)

    context = {
        "meetingtype": meetingtype,
        "function": function,
        "form": form,
    }
    return render(request, "persons/del_function.html", context)


# delete function (allowed only by meetingtype-admin or staff)
