import magic

from django.shortcuts import render as django_render
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from meetingtypes.models import MeetingType


def render(request, template, context):
    if 'meetingtype' in context:
        context['active_meetingtype'] = context['meetingtype']
    elif 'meeting' in context:
        context['active_meetingtype'] = context['meeting'].meetingtype

    if 'meetingtypes' not in context:
        meetingtypes = MeetingType.objects.order_by('name')
        context['meetingtypes'] = meetingtypes

    return django_render(request, template, context)


def validate_file_type(upload):
    filetype = magic.from_buffer(upload.file.read(1024), mime=True)
    if filetype not in settings.ALLOWED_FILE_TYPES:
        raise ValidationError(
            _('Der Dateityp wird nicht unterstützt. Es können nur PDFs ' \
                'hochgeladen werden'))
