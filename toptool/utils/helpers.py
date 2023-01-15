from uuid import UUID

from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404

from meetings.models import Meeting


def get_meeting_or_404_on_validation_error(meeting_pk: UUID) -> Meeting:
    """
    @param meeting_pk: the meetings uuid
    @return: the meeting with the given pk or raises Http404 if the pk is invalid
    """
    try:
        return get_object_or_404(Meeting, pk=meeting_pk)
    except ValidationError as error:
        raise Http404 from error


def get_meeting_from_qs_or_404_on_validation_error(
    query_set: QuerySet[Meeting],
    meeting_pk: UUID,
) -> Meeting:
    """
    @param query_set: the queryset to filter the meeting from
    @param meeting_pk: the meetings uuid
    @return: the meeting with the given pk or raises Http404 if the pk is invalid
    """
    try:
        return get_object_or_404(query_set, pk=meeting_pk)
    except ValidationError as error:
        raise Http404 from error
