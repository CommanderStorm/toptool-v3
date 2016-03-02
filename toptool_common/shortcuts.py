from django.shortcuts import render as django_render

from meetingtypes.models import MeetingType

def render(request, template, context):
    meetingtypes = MeetingType.objects.order_by('name')

    if 'meetingtypes' not in context:
        context['meetingtypes'] = meetingtypes

    return django_render(request, template, context)

