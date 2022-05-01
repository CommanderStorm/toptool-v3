from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.handlers.wsgi import WSGIRequest
from django_compref_keycloak.decorators import federation_no_shibboleth_required

from meetings.models import Meeting
from meetingtypes.models import MeetingType
from toptool.utils.typing import AuthWSGIRequest

# Our permission order is the following:
# staff < admin of the meeting < sitzungsleitung < minute_taker


def at_least_admin(request: AuthWSGIRequest | WSGIRequest, meetingtype: MeetingType) -> bool:
    """
    admin of the meeting or staff.
    @param request: the request, which has to be checked
    @param meetingtype: the meetingtype, which this request has to be checked for
    @return: authorization result
    """
    return request.user.has_perm(meetingtype.admin_permission()) or request.user.is_staff


def at_least_sitzungsleitung(request: WSGIRequest, meeting: Meeting) -> bool:
    """
    at_least_admin or sitzungsleitung.
    @param request: the request, which has to be checked
    @param meeting: the meeting, which this request has to be checked for
    @return: authorization result
    """
    return at_least_admin(request, meeting.meetingtype) or request.user == meeting.sitzungsleitung


def at_least_minute_taker(
    request: AuthWSGIRequest,
    meeting: Meeting,
    require_mt_protokoll_for_meeting_taker: bool = False,
) -> bool:
    """
    at_least_admin or minute_taker.
    @param request: the request, which has to be checked
    @param meeting: the meeting, which this request has to be checked for
    @param require_mt_protokoll_for_meeting_taker: if True, the user is only a valid minute taker,
     if the mt is also a protokoll
    @return: authorization result
    """
    minute_taker = request.user in meeting.minute_takers.all()
    if require_mt_protokoll_for_meeting_taker:
        minute_taker = minute_taker and meeting.meetingtype.protokoll
    return at_least_sitzungsleitung(request, meeting) or minute_taker


def require(check: bool) -> None:
    """
    Raises a PermissionDenied exception if check is False.
    @param check: the parameter to check
    @return: None
    """
    if not check:
        raise PermissionDenied


def auth_login_required():
    """correct login_required decorator, depending on settings.USE_KEYCLOAK"""
    if settings.USE_KEYCLOAK:
        return federation_no_shibboleth_required()
    return login_required()
