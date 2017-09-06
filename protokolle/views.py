from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django import forms
from django.conf import settings
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from meetings.models import Meeting
from meetingtypes.models import MeetingType
from toptool_common.shortcuts import render
from .models import Protokoll, protokoll_path
from .forms import ProtokollForm


# download empty template (only allowed by users with permission for the
# meetingtype)
@login_required
def template(request, mt_pk, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not request.user.has_perm(meeting.meetingtype.permission()):
        raise PermissionDenied
    elif meeting.imported:
        raise PermissionDenied

    tops = meeting.top_set.order_by('topid')

    response = HttpResponse(content_type='text/t2t')
    response['Content-Disposition'] = \
        'attachment; filename=protokoll_{0:04}_{1:02}_{2:02}.t2t'.format(
            meeting.time.year,
            meeting.time.month,
            meeting.time.day,
        )

    text_template = get_template('protokolle/vorlage.t2t')
    context = {
        'meeting': meeting,
        'tops': tops,
    }

    response.write(text_template.render(context))
    return response


# download previously uploaded template (only allowed by meetingtype-admin,
# sitzungsleitung and protokollant)
@login_required
def template_filled(request, mt_pk, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung or
            request.user == meeting.protokollant):
        raise PermissionDenied
    elif meeting.imported:
        raise PermissionDenied

    protokoll = get_object_or_404(Protokoll, meeting=meeting_pk)

    response = HttpResponse(content_type='text/t2t')
    response['Content-Disposition'] = 'attachment; filename=' + \
        protokoll.filename + ".t2t"

    protokoll.t2t.open('r')
    response.write(protokoll.t2t.read())
    return response


# show protokoll by type (allowed only by users with permission for the
# meetingtype)
# if the user is not logged in and the public bit is set and the protokoll is
# approved, this redirects to show_public_protokoll
def show_protokoll(request, mt_pk, meeting_pk, filetype):
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    meeting = get_object_or_404(meetingtype.meeting_set, pk=meeting_pk)
    protokoll = get_object_or_404(Protokoll, meeting=meeting_pk)
    if not meeting.meetingtype.public or not protokoll.approved:
        # public access disabled or protokoll not approved yet
        if not request.user.is_authenticated():
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        if not request.user.has_perm(meeting.meetingtype.permission()):
            raise PermissionDenied
    elif not request.user.is_authenticated():
        return redirect('protokollpublic', mt_pk, meeting_pk, filetype)

    if filetype == "txt":
        response = HttpResponse(content_type='text/plain')
    elif filetype == "html":
        response = HttpResponse()
    elif filetype == "pdf":
        response = HttpResponse(content_type='application/pdf')
    else:
        raise Http404("Invalid filetype")

    with open(protokoll.filepath + "." + filetype, "rb") as f:
        response.write(f.read())
    return response


# show public protokoll by type (allowed for public if public-bit set and
# protokoll approved)
# note: the server configuration should add a shibboleth authentication,
#       otherwise the protokoll is publicly available (if public-bit set)
def show_public_protokoll(request, mt_pk, meeting_pk, filetype):
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    meeting = get_object_or_404(meetingtype.meeting_set, pk=meeting_pk)
    protokoll = get_object_or_404(Protokoll, meeting=meeting_pk)
    if not meeting.meetingtype.public or not protokoll.approved:
        return redirect('protokoll', mt_pk, meeting_pk, filetype)

    if filetype == "txt":
        response = HttpResponse(content_type='text/plain')
    elif filetype == "html":
        response = HttpResponse()
    elif filetype == "pdf":
        response = HttpResponse(content_type='application/pdf')
    else:
        raise Http404("Invalid filetype")

    with open(protokoll.filepath + "." + filetype, "rb") as f:
        response.write(f.read())
    return response


# edit/add protokoll (if protokoll exists only allowed by meetingtype-admin,
# sitzungsleitung and protokollant, otherwise only allowed by users with
# permission for the meetingtype)
@login_required
def edit_protokoll(request, mt_pk, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if meeting.protokollant:
        if not (request.user.has_perm(
                meeting.meetingtype.admin_permission()) or
                request.user == meeting.sitzungsleitung or
                request.user == meeting.protokollant):
            raise PermissionDenied
    elif not request.user.has_perm(meeting.meetingtype.permission()):
        raise PermissionDenied
    elif meeting.imported:
        raise PermissionDenied

    try:
        protokoll = meeting.protokoll
        exists = True
    except Protokoll.DoesNotExist:
        protokoll = None
        exists = False

    initial = {
        'sitzungsleitung': meeting.sitzungsleitung,
    }
    t2t = None
    if protokoll:
        initial.update({
            'begin': protokoll.begin,
            'end': protokoll.end,
            'approved': protokoll.approved,
        })
        t2t = protokoll.t2t

    if not meeting.meetingtype.approve:
        initial['approved'] = True

    users = User.objects.filter(
        Q(user_permissions=meeting.meetingtype.get_permission()) |
        Q(groups__permissions=meeting.meetingtype.get_permission())
        ).distinct().order_by('first_name', 'last_name', 'username')

    form = ProtokollForm(
        request.POST or None,
        request.FILES or None,
        instance=protokoll,
        initial=initial,
        users=users,
        meeting=meeting,
        t2t=t2t,
    )
    if form.is_valid():
        form.save()

        if not meeting.sitzungsleitung:
            Meeting.objects.filter(pk=meeting_pk).update(
                sitzungsleitung=form.cleaned_data['sitzungsleitung'],
            )
        if not meeting.protokollant:
            Meeting.objects.filter(pk=meeting_pk).update(
                protokollant=request.user,
            )

        meeting = get_object_or_404(Meeting, pk=meeting_pk)

        if meeting.protokoll.t2t:
            if 'protokoll' in request.FILES:
                meeting.protokoll.t2t.open('wb')
                meeting.protokoll.t2t.close()
                meeting.protokoll.t2t.open('wb')
                for c in request.FILES['protokoll'].chunks():
                    meeting.protokoll.t2t.write(c)
                meeting.protokoll.t2t.close()
        else:
            meeting.protokoll.t2t.save(
                protokoll_path(meeting.protokoll, "protokoll.t2t"),
                request.FILES['protokoll'])

        try:
            meeting.protokoll.generate()
        except UnicodeDecodeError:
            messages.error(request,
                _('Encoding-Fehler: Die Protokoll-Datei ist nicht UTF-8 kodiert.')
            )
        except RuntimeError as e:
            lines = e.args[0].decode('utf-8').strip().splitlines()
            if lines[-1].startswith("txt2tags.error"):
                messages.error(request,
                    lines[-1]
                )
            else:
                raise e
        else:
            return redirect('successprotokoll', meeting.meetingtype.id, meeting.id)

    delete = (request.user.has_perm(meeting.meetingtype.admin_permission()) or
              request.user == meeting.sitzungsleitung or
              request.user == meeting.protokollant) and exists

    context = {'meeting': meeting,
               'delete': delete,
               'exists': exists,
               'form': form}
    return render(request, 'protokolle/edit.html', context)


# success protokoll (only allowed by meetingtype-admin, sitzungsleitung and
# protokollant)
@login_required
def success_protokoll(request, mt_pk, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung or
            request.user == meeting.protokollant):
        raise PermissionDenied
    elif meeting.imported:
        raise PermissionDenied

    protokoll = get_object_or_404(Protokoll, pk=meeting_pk)

    context = {'meeting': meeting,
               'protokoll': protokoll}
    return render(request, 'protokolle/success.html', context)


# success protokoll (only allowed by meetingtype-admin, sitzungsleitung
# protokollant)
@login_required
def delete_protokoll(request, mt_pk, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung or
            request.user == meeting.protokollant):
        raise PermissionDenied

    protokoll = get_object_or_404(Protokoll, pk=meeting_pk)

    form = forms.Form(request.POST or None)
    if form.is_valid():
        Protokoll.objects.filter(pk=meeting_pk).delete()
        return redirect('viewmeeting', meeting.meetingtype.id, meeting.id)

    context = {'meeting': meeting,
               'protokoll': protokoll,
               'form': form}
    return render(request, 'protokolle/del.html', context)


# send protokoll to mailing list (only allowed by meetingtype-admin,
# sitzungsleitung, protokollant)
@login_required
def send_protokoll(request, mt_pk, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung or
            request.user == meeting.protokollant):
        raise PermissionDenied
    elif meeting.imported:
        raise PermissionDenied

    protokoll = get_object_or_404(Protokoll, pk=meeting_pk)
    subject, text, from_email, to_email = protokoll.get_mail(request)

    form = forms.Form(request.POST or None)
    if form.is_valid():
        send_mail(subject, text, from_email, [to_email], fail_silently=False)
        return redirect('viewmeeting', meeting.meetingtype.id, meeting.id)

    context = {'meeting': meeting,
               'protokoll': protokoll,
               'subject': subject,
               'text': text,
               'from_email': from_email,
               'to_email': to_email,
               'form': form}
    return render(request, 'protokolle/send_mail.html', context)
