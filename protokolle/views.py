from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template

def template(request, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    tops = meeting.top_set.order_by('topid')

    # Create the HttpResponse object with the appropriate t2t header.
    response = HttpResponse(content_type='text/t2t')

    # TODO: add date etc. to default name?
    response['Content-Disposition'] = 'attachment; filename=protokoll.t2t"'

    text_template = get_template('protokolle/vorlage.t2t')
    context = {
        'meeting': meeting,
        'tops': tops,
    }

    response.write(text_template.render(context))
    return response

def protokoll(request, meeting_pk, filetype):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    # TODO


