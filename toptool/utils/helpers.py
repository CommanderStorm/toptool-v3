from uuid import UUID

from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404

from meetings.models import Meeting


def get_meeting_or_404_on_validation_error(meeting_pk: UUID) -> Meeting:
    try:
        return get_object_or_404(Meeting, pk=meeting_pk)
    except ValidationError as error:
        raise Http404 from error


def get_meeting_from_qs_or_404_on_validation_error(
    querry_set: QuerySet[Meeting],
    meeting_pk: UUID,
) -> Meeting:
    try:
        return get_object_or_404(querry_set, pk=meeting_pk)
    except ValidationError as error:
        raise Http404 from error
