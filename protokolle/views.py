from wsgiref.util import FileWrapper
import datetime
import os.path
from urllib.error import URLError
from py_etherpad import EtherpadLiteClient

from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseBadRequest, HttpResponse, Http404
from django.http.response import JsonResponse
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
from django.template import TemplateSyntaxError
from django.core.files.base import ContentFile
from django.utils import timezone

from meetings.models import Meeting
from meetingtypes.models import MeetingType
from toptool.shortcuts import render
from .models import Protokoll, Attachment, protokoll_path
from .forms import ProtokollForm, AttachmentForm, TemplatesForm, PadForm


# download an empty or filled template (only allowed by
# meetingtype-admin, sitzungsleitung and protokollant)
@login_required
def templates(request, mt_pk, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not (request.user.has_perm(
            meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung or
            request.user == meeting.protokollant):
        raise PermissionDenied
    elif meeting.imported:
        raise PermissionDenied

    if not meeting.meetingtype.protokoll:
        raise Http404

    try:
        protokoll = meeting.protokoll
    except Protokoll.DoesNotExist:
        protokoll = None

    last_edit_pad = None
    if meeting.meetingtype.pad and meeting.pad:
        pad_client = EtherpadLiteClient(
            settings.ETHERPAD_APIKEY, settings.ETHERPAD_API_URL)
        try:
            last_edit_pad = datetime.datetime.fromtimestamp(
                pad_client.getLastEdited(meeting.pad)['lastEdited']/1000
            )
        except (URLError, KeyError, ValueError):
            last_edit_pad = None

    last_edit_file = None
    if protokoll and protokoll.t2t:
        last_edit_file = datetime.datetime.fromtimestamp(
            os.path.getmtime(protokoll.t2t.path)
        )

    if last_edit_pad is None and last_edit_file is None:
        initial_source = 'template'
    elif last_edit_pad is None:
        initial_source = 'file'
    elif last_edit_file is None:
        initial_source = 'pad'
    elif last_edit_file >= last_edit_pad:
        initial_source = 'file'
    else:
        initial_source = 'pad'

    os_family = 'unix'
    try:
        if "Windows" in request.user_agent.os.family:
            os_family = 'win'
    except AttributeError:
        pass

    form = TemplatesForm(
        request.POST or None,
        last_edit_pad=last_edit_pad,
        last_edit_file=last_edit_file,
        initial={
            'line_breaks': os_family,
            'source': initial_source,
        },
    )
    if form.is_valid():
        text = None
        source = form.cleaned_data["source"]
        if source == 'pad' and meeting.meetingtype.pad and meeting.pad:
            try:
                text = pad_client.getText(meeting.pad)["text"]
            except (URLError, KeyError, ValueError):
                messages.error(
                    request, _('Interner Server Fehler: Pad nicht erreichbar.')
                )
        elif source == 'file' and protokoll and protokoll.t2t:
            protokoll.t2t.open('r')
            text = protokoll.t2t.read()
        elif source == 'template':
            tops = meeting.get_tops_with_id()
            text_template = get_template('protokolle/vorlage.t2t')
            context = {
                'meeting': meeting,
                'tops': tops,
            }
            text = text_template.render(context)

        if text:
            line_break = form.cleaned_data["line_breaks"]
            if line_break == "win":
                text = text.replace("\n", "\r\n")

            response = HttpResponse(content_type='text/t2t')
            response['Content-Disposition'] = \
                'attachment; filename=protokoll_{0:04}_{1:02}_{2:02}.t2t'.format(
                    meeting.time.year,
                    meeting.time.month,
                    meeting.time.day,
                )
            response.write(text)
            return response

    context = {'meeting': meeting,
               'last_edit_file': last_edit_file,
               'last_edit_pad': last_edit_pad,
               'form': form}
    return render(request, 'protokolle/templates.html', context)


# open template in etherpad (only allowed by meetingtype-admin,
# sitzungsleitung and protokollant)
@login_required
def pad(request, mt_pk, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung or
            request.user == meeting.protokollant):
        raise PermissionDenied
    elif meeting.imported:
        raise PermissionDenied

    if not meeting.meetingtype.pad or not meeting.meetingtype.protokoll:
        raise Http404

    try:
        protokoll = meeting.protokoll
    except Protokoll.DoesNotExist:
        protokoll = None

    pad_client = EtherpadLiteClient(settings.ETHERPAD_APIKEY, settings.ETHERPAD_API_URL)
    try:
        group_id = pad_client.createGroupIfNotExistsFor(groupMapper=meeting.pk)["groupID"]
        if not meeting.pad:
            if protokoll:
                protokoll.t2t.open('r')
                text = protokoll.t2t.read()
            else:
                text_template = get_template('protokolle/vorlage.t2t')
                tops = meeting.get_tops_with_id()
                context = {
                    'meeting': meeting,
                    'tops': tops,
                }
                text = text_template.render(context)
            name = "protokoll"
            pad_client.createGroupPad(group_id, name, text)
            meeting.pad = "{}${}".format(group_id, name)
            meeting.save()
        author_id = pad_client.createAuthorIfNotExistsFor(
            request.user.username, request.user.first_name)["authorID"]
        valid_until = datetime.datetime.now() + datetime.timedelta(hours=7)
        session_id = pad_client.createSession(
            group_id, author_id, int(valid_until.timestamp()))["sessionID"]
        url = settings.ETHERPAD_PAD_URL
    except (URLError, ValueError):
        url = None
        session_id = None

    form = None
    if url:
        last_edit_file = None
        if protokoll and protokoll.t2t:
            last_edit_file = datetime.datetime.fromtimestamp(
                os.path.getmtime(protokoll.t2t.path)
            )

        if last_edit_file is None:
            initial_source = 'upload'
        else:
            initial_source = 'file'

        form = PadForm(
            request.POST or None,
            request.FILES or None,
            last_edit_file=last_edit_file,
            initial={
                'source': initial_source,
            },
        )
        if form.is_valid():
            text = None
            source = form.cleaned_data["source"]
            if source == "file":
                protokoll.t2t.open('r')
                text = protokoll.t2t.read()
            elif source == "upload":
                if 'template_file' in request.FILES:
                    text = request.FILES['template_file'].read()
            elif source == "template":
                tops = meeting.get_tops_with_id()
                text_template = get_template('protokolle/vorlage.t2t')
                context = {
                    'meeting': meeting,
                    'tops': tops,
                }
                text = text_template.render(context)

            try:
                pad_client.setText(meeting.pad, text)
            except (URLError, ValueError):
                messages.error(
                    request,
                    _('Interner Server Fehler: Text kann nicht ins Pad geladen werden werden.')
                )
            else:
                return redirect("pad", meeting.meetingtype.pk, meeting.pk)

    context = {'meeting': meeting,
               'url': url,
               'form': form}
    response = render(request, 'protokolle/pad.html', context)
    if session_id:
        response.set_cookie('sessionID', session_id, path="/",
                            domain=settings.ETHERPAD_DOMAIN)
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
    elif not meeting.meetingtype.protokoll:
        raise Http404
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

    if not meeting.meetingtype.protokoll:
        raise Http404

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


# edit/add protokoll (only allowed by meetingtype-admin, sitzungsleitung
# and protokollant)
@login_required
def edit_protokoll(request, mt_pk, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung or
            request.user == meeting.protokollant):
        raise PermissionDenied
    elif meeting.imported:
        raise PermissionDenied

    if not meeting.meetingtype.protokoll:
        raise Http404

    try:
        protokoll = meeting.protokoll
    except Protokoll.DoesNotExist:
        protokoll = None

    last_edit_pad = None
    if meeting.meetingtype.pad and meeting.pad:
        pad_client = EtherpadLiteClient(
            settings.ETHERPAD_APIKEY, settings.ETHERPAD_API_URL)
        try:
            last_edit_pad = datetime.datetime.fromtimestamp(
                pad_client.getLastEdited(meeting.pad)['lastEdited']/1000
            )
        except (URLError, KeyError, ValueError):
            last_edit_pad = None

    t2t = None
    last_edit_file = None
    if protokoll and protokoll.t2t:
        t2t = protokoll.t2t
        last_edit_file = datetime.datetime.fromtimestamp(
            os.path.getmtime(protokoll.t2t.path)
        )

    if last_edit_pad is None:
        initial_source = 'upload'
    elif last_edit_file is None:
        initial_source = 'pad'
    elif last_edit_pad >= last_edit_file:
        initial_source = 'pad'
    else:
        initial_source = 'upload'

    initial = {
        'sitzungsleitung': meeting.sitzungsleitung,
        'source': initial_source,
        'begin': timezone.localtime(meeting.time).timetz(),
        'end': (timezone.localtime(meeting.time) + datetime.timedelta(hours=2)).timetz(),
    }
    if not protokoll and not meeting.meetingtype.approve:
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
        last_edit_pad=last_edit_pad,
        last_edit_file=last_edit_file,
    )
    if form.is_valid():
        text = None
        source = form.cleaned_data["source"]
        if source == "pad" and meeting.meetingtype.pad and meeting.pad:
            try:
                text = pad_client.getText(meeting.pad)["text"]
            except (URLError, KeyError, ValueError):
                messages.error(
                    request, _('Interner Server Fehler: Pad nicht erreichbar.')
                )
        elif source == "file" and t2t:
            text = "__file__"
        elif source == "upload":
            if 'protokoll' in request.FILES:
                text = request.FILES['protokoll'].read().decode("utf8")

        if text:
            form.save()
            if not meeting.sitzungsleitung:
                meeting.sitzungsleitung = form.cleaned_data['sitzungsleitung']
            if not meeting.protokollant:
                meeting.protokollant = request.user
            meeting.save()
            if text != "__file__":
                if meeting.protokoll.t2t:
                    meeting.protokoll.t2t.open('w')
                    meeting.protokoll.t2t.close()
                    meeting.protokoll.t2t.open('w')
                    meeting.protokoll.t2t.write(text)
                    meeting.protokoll.t2t.close()
                else:
                    meeting.protokoll.t2t.save(
                        protokoll_path(meeting.protokoll, "protokoll.t2t"),
                        ContentFile(text))

            try:
                meeting.protokoll.generate(request)
            except TemplateSyntaxError as err:
                messages.error(
                    request, _('Template-Syntaxfehler: ') + err.args[0]
                )
            except UnicodeDecodeError:
                messages.error(
                    request,
                    _('Encoding-Fehler: Die Protokoll-Datei ist nicht UTF-8 kodiert.')
                )
            except RuntimeError as err:
                lines = err.args[0].decode('utf-8').strip().splitlines()
                if lines[-1].startswith("txt2tags.error"):
                    messages.error(request, lines[-1])
                else:
                    if not protokoll:
                        meeting.protokoll.delete()
                    raise err
            else:
                return redirect('successprotokoll', meeting.meetingtype.id, meeting.id)
            # if not successful: delete protokoll
            if not protokoll:
                meeting.protokoll.delete()

    context = {'meeting': meeting,
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

    if not meeting.meetingtype.protokoll:
        raise Http404

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

    if not meeting.meetingtype.protokoll:
        raise Http404

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

    if not meeting.meetingtype.protokoll:
        raise Http404

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


# add, edit or remove attachments to protokoll (allowed only by
# meetingtype-admin, sitzungsleitung or protokollant)
@login_required
def attachments(request, mt_pk, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not (request.user.has_perm(meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung or
            request.user == meeting.protokollant):
        raise PermissionDenied
    elif meeting.imported:
        raise PermissionDenied

    if not meeting.meetingtype.protokoll or not meeting.meetingtype.attachment_protokoll:
        raise Http404

    attachment_list = Attachment.objects.filter(meeting=meeting).order_by(
        'sort_order', 'name')

    if request.method == "POST":
        form = AttachmentForm(request.POST, request.FILES, meeting=meeting)
        if form.is_valid():
            form.save()
            return redirect('attachments', meeting.meetingtype.id, meeting.id)
    else:
        form = AttachmentForm(meeting=meeting)

    context = {'meeting': meeting,
               'attachments': attachment_list,
               'form': form}
    return render(request, 'protokolle/attachments.html', context)


# sort attachments for protokoll (allowed only by meetingtype-admin,
# sitzungsleitung or protokollant)
@login_required
def sort_attachments(request, mt_pk, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not (request.user.has_perm(
            meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung or
            request.user == meeting.protokollant):
        raise PermissionDenied
    elif meeting.imported:
        raise PermissionDenied

    if not meeting.meetingtype.protokoll or not meeting.meetingtype.attachment_protokoll:
        raise Http404

    if request.method == "POST":
        attachment_list = request.POST.getlist("attachments[]", None)
        attachment_list = [t for t in attachment_list if t]
        if attachment_list:
            for i, attach in enumerate(attachment_list):
                try:
                    attach_pk = int(attach.partition("_")[2])
                except (ValueError, IndexError):
                    return HttpResponseBadRequest('')
                try:
                    attach = Attachment.objects.get(pk=attach_pk)
                except Attachment.DoesNotExist:
                    return HttpResponseBadRequest('')
                attach.sort_order = i
                attach.save()
            return JsonResponse({'success': True})

    return HttpResponseBadRequest('')


# show protokoll attachment (allowed only by users with permission for the
# meetingtype)
@login_required
def show_attachment(request, mt_pk, meeting_pk, attachment_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not request.user.has_perm(meeting.meetingtype.permission()):
        raise PermissionDenied
    if meeting.imported:
        raise PermissionDenied

    if not meeting.meetingtype.protokoll or not meeting.meetingtype.attachment_protokoll:
        raise Http404

    attachment = get_object_or_404(meeting.attachment_set, pk=attachment_pk)
    filename = attachment.attachment.path
    wrapper = FileWrapper(open(filename, 'rb'))
    response = HttpResponse(wrapper, content_type='application/pdf')

    return response


# edit a protokoll attachment (allowed only by meetingtype-admin,
# sitzungsleitung or protokollant)
@login_required
def edit_attachment(request, mt_pk, meeting_pk, attachment_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not (request.user.has_perm(
            meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung or
            request.user == meeting.protokollant):
        raise PermissionDenied
    elif meeting.imported:
        raise PermissionDenied

    if not meeting.meetingtype.protokoll or not meeting.meetingtype.attachment_protokoll:
        raise Http404

    attachment = get_object_or_404(meeting.attachment_set, pk=attachment_pk)

    if request.method == "POST":
        form = AttachmentForm(request.POST, request.FILES, meeting=meeting,
                              instance=attachment)
        if form.is_valid():
            form.save()
            return redirect('attachments', meeting.meetingtype.id, meeting.id)
    else:
        form = AttachmentForm(meeting=meeting, instance=attachment)

    context = {'meeting': meeting,
               'attachment': attachment,
               'form': form}
    return render(request, 'protokolle/edit_attachment.html', context)


# delete a protokoll attachment (allowed only by meetingtype-admin,
# sitzungsleitung or protokollant)
@login_required
def delete_attachment(request, mt_pk, meeting_pk, attachment_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not (request.user.has_perm(
            meeting.meetingtype.admin_permission()) or
            request.user == meeting.sitzungsleitung or
            request.user == meeting.protokollant):
        raise PermissionDenied
    elif meeting.imported:
        raise PermissionDenied

    if not meeting.meetingtype.protokoll or not meeting.meetingtype.attachment_protokoll:
        raise Http404

    attachment = get_object_or_404(meeting.attachment_set, pk=attachment_pk)

    form = forms.Form(request.POST or None)
    if form.is_valid():
        attachment.delete()
        return redirect('attachments', meeting.meetingtype.id, meeting.id)

    context = {'meeting': meeting,
               'attachment': attachment,
               'form': form}
    return render(request, 'protokolle/delete_attachment.html', context)
