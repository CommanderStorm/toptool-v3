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

    if 'meeting_today' not in context:
        meetingtypes = MeetingType.objects.all()
        meetings_today = []
        for meetingtype in meetingtypes:
            if request.user.has_perm(meetingtype.permission()):
                meetings_today.extend(meetingtype.today)
        meetings_today = filter(lambda m: m.time > timezone.now(),
            meetings_today)
        meetings_today = sorted(meetings_today, key=lambda m: m.time)
        if meetings_today:
            context['meeting_today'] = meetings_today[0]
        else:
            context['meeting_today'] = None

    if 'meeting_tomorrow' not in context:
        if context['meeting_today']:
            context['meeting_tomorrow'] = None
        else:
            meetingtypes = MeetingType.objects.all()
            meetings_tomorrow = []
            for meetingtype in meetingtypes:
                if request.user.has_perm(meetingtype.permission()):
                    meetings_tomorrow.extend(meetingtype.tomorrow)
            meetings_tomorrow = sorted(meetings_tomorrow, key=lambda m: m.time)
            if meetings_tomorrow:
                context['meeting_tomorrow'] = meetings_tomorrow[0]
            else:
                context['meeting_tomorrow'] = None

    return django_render(request, template, context)


def validate_file_type(upload):
    filetype = magic.from_buffer(upload.file.read(1024), mime=True)
    if filetype not in settings.ALLOWED_FILE_TYPES:
        raise ValidationError(
            _('Der Dateityp wird nicht unterstützt. Es können nur PDFs ' \
                'hochgeladen werden'))
