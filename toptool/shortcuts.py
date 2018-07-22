import magic

from django.shortcuts import render as django_render
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from meetingtypes.models import MeetingType


def render(request, template, context):
    if 'meetingtype' in context:
        context['active_meetingtype'] = context['meetingtype']
    elif 'meeting' in context:
        context['active_meetingtype'] = context['meeting'].meetingtype

    if 'meetingtypes' not in context and request.user.is_authenticated():
        meetingtypes = MeetingType.objects.order_by('name')
        mts_with_perm = []
        for meetingtype in meetingtypes:
            if request.user.has_perm(meetingtype.permission()):
                mts_with_perm.append(meetingtype)
        mt_preferences = {
            mtp.meetingtype.pk: mtp.sortid for mtp in
            request.user.meetingtypepreference_set.all()
        }
        if mt_preferences:
            max_sortid = max(mt_preferences.values()) + 1
        else:
            max_sortid = 1
        mts_with_perm.sort(
            key=lambda mt: (mt_preferences.get(mt.pk, max_sortid), mt.name)
        )
        context['meetingtypes'] = mts_with_perm[:3]

    return django_render(request, template, context)


def validate_file_type(upload):
    filetype = magic.from_buffer(upload.file.read(1024), mime=True)
    if filetype not in settings.ALLOWED_FILE_TYPES.values():
        raise ValidationError(
            _('Der Dateityp wird nicht unterstützt. Es können nur folgende '
              'Dateitypen hochgeladen werden: %(filetypes)s') %
            {"filetypes": ", ".join(settings.ALLOWED_FILE_TYPES.keys())})
