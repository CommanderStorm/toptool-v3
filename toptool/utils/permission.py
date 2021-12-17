from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.handlers.wsgi import WSGIRequest
from django_compref_keycloak.decorators import federation_no_shibboleth_required

from meetings.models import Meeting
from meetingtypes.models import MeetingType
from toptool.utils.typing import AuthWSGIRequest


def is_admin_staff(request: AuthWSGIRequest, meetingtype: MeetingType) -> bool:
    return request.user.has_perm(meetingtype.admin_permission()) or request.user.is_staff


def is_admin_sitzungsleitung_minute_takers(request: AuthWSGIRequest, meeting: Meeting) -> bool:
    minute_taker = request.user in meeting.minute_takers.all()
    return is_admin_sitzungsleitung(request, meeting) or minute_taker


def is_admin_sitzungsleitung_protokoll_minute_takers(request: AuthWSGIRequest, meeting: Meeting) -> bool:
    minute_taker = meeting.meetingtype.protokoll and request.user in meeting.minute_takers.all()
    return is_admin_sitzungsleitung(request, meeting) or minute_taker


def is_admin_sitzungsleitung(request: WSGIRequest, meeting: Meeting) -> bool:
    return request.user.has_perm(meeting.meetingtype.admin_permission()) or request.user == meeting.sitzungsleitung


def require(check: bool) -> None:
    if not check:
        raise PermissionDenied


def auth_login_required():
    if settings.USE_KEYCLOAK:
        return federation_no_shibboleth_required()
    return login_required()
