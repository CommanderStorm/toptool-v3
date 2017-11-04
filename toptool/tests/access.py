import pytest
from mixer.backend.django import mixer

from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.core.files.uploadedfile import SimpleUploadedFile

from meetingtypes.models import MeetingType
from meetings.models import Meeting
from tops.models import Top, StandardTop

pytestmark = pytest.mark.django_db


def redirect_to_login(url, redirect_url, view, *args):
    resp = view(*args)
    assert resp.status_code == 302, 'Should redirect to login'
    assert resp.url == '/login/?next=' + url, 'Should redirect to login'

def redirect_to_url(url, redirect_url, view, *args):
    resp = view(*args)
    assert resp.status_code == 302, 'Should redirect to given url'
    assert resp.url == redirect_url, 'Should redirect to given url'

def accessible(url, redirect_url, view, *args):
    resp = view(*args)
    assert resp.status_code == 200, 'Should be accessible'

def permission_denied(url, redirect_url, view, *args):
    with pytest.raises(PermissionDenied):
        resp = view(*args)

def not_found(url, redirect_url, view, *args):
    with pytest.raises((Http404, AssertionError)):
        resp = view(*args)
        assert resp.status_code == 404, 'Should be a 404 - not found'

def bad_request(url, redirect_url, view, *args):
    resp = view(*args)
    assert resp.status_code == 400, 'Should be a 400 - bad request'

class AbstractTestView:
    def setup_method(self):
        self.anonymous_public = None
        self.anonymous_not_public = None
        self.logged_in_public = None
        self.logged_in_with_rights = None
        self.logged_in_with_admin_rights = None
        self.logged_in_without_rights = None
        self.logged_in_sitzungsleitung = None
        self.logged_in_protokollant = None
        self.admin_public = None
        self.admin_not_public = None
        self.args = []
        self.redirect_url = None
        self.use_meeting = True
        self.use_meeting_for_redirect = False
        self.use_top = False
        self.use_std_top = False

    @pytest.fixture(autouse=True)
    def prepare_variables(self):
        self.mt = mixer.blend(MeetingType, id="abc", public=False)
        self.mt2 = mixer.blend(MeetingType, id="abcd", public=False)
        self.meeting = mixer.blend(Meeting, meetingtype=self.mt)
        self.top = mixer.blend(Top, meeting=self.meeting)
        self.top.attachment = SimpleUploadedFile("test.pdf", b'Test Inhalt')
        self.top.save()
        self.std_top = mixer.blend(StandardTop, meetingtype=self.mt)
        content_type = ContentType.objects.get_for_model(MeetingType)
        self.permission = Permission.objects.get_or_create(codename=self.mt.pk,
            content_type=content_type)[0]
        self.admin_permission = Permission.objects.get_or_create(
            codename=self.mt.pk + MeetingType.ADMIN,
            content_type=content_type)[0]
        self.permission2 = Permission.objects.get_or_create(
            codename=self.mt2.pk, content_type=content_type)[0]
        self.admin_permission2 = Permission.objects.get_or_create(
            codename=self.mt2.pk + MeetingType.ADMIN,
            content_type=content_type)[0]
        self.anonymous_user = AnonymousUser()
        self.logged_in_user = mixer.blend('auth.User',
                is_registered_user=True, is_superuser=False)
        self.admin_user = mixer.blend('auth.User',
                is_registered_user=True, is_superuser=True)

    def check_response_with_user(self, user, check_result):
        if self.use_std_top:
            args = [self.mt.pk, self.std_top.pk] + self.args
        elif self.use_top:
            args = [self.mt.pk, self.meeting.pk, self.top.pk] + self.args
        elif self.use_meeting:
            args = [self.mt.pk, self.meeting.pk] + self.args
        else:
            args = [self.mt.pk] + self.args
        url = self.url.format(*args)
        if self.redirect_url is not None:
            if not self.use_meeting and self.use_meeting_for_redirect:
                t_args = [self.mt.pk, self.meeting.pk] + self.args
            else:
                t_args = args
            redirect_url = self.redirect_url.format(*t_args)
        else:
            redirect_url = None
        req = RequestFactory().get(url)
        req.user = user
        check_result(url, redirect_url, self.view, req, *args)

    def test_anonymous_public(self):
        if self.anonymous_public is None:
            return
        self.prepare_variables()
        self.mt.public = True
        self.mt.save()
        self.check_response_with_user(self.anonymous_user,
            self.anonymous_public)

    def test_anonymous_not_public(self):
        if self.anonymous_not_public is None:
            return
        self.prepare_variables()
        self.check_response_with_user(self.anonymous_user,
            self.anonymous_not_public)

    def test_logged_in_public(self):
        if self.logged_in_public is None:
            return
        self.prepare_variables()
        self.mt.public = True
        self.mt.save()
        self.check_response_with_user(self.logged_in_user,
            self.logged_in_public)

    def test_logged_in_with_rights(self):
        if self.logged_in_with_rights is None:
            return
        self.prepare_variables()
        self.logged_in_user.user_permissions.add(self.permission)
        self.check_response_with_user(self.logged_in_user,
            self.logged_in_with_rights)

    def test_logged_in_with_admin_rights(self):
        if self.logged_in_with_admin_rights is None:
            return
        self.prepare_variables()
        self.logged_in_user.user_permissions.add(self.admin_permission)
        self.check_response_with_user(self.logged_in_user,
            self.logged_in_with_admin_rights)

    def test_logged_in_without_rights(self):
        if self.logged_in_without_rights is None:
            return
        self.prepare_variables()
        self.check_response_with_user(self.logged_in_user,
            self.logged_in_without_rights)

    def test_logged_in_sitzungsleitung(self):
        if self.logged_in_sitzungsleitung is None:
            return
        self.prepare_variables()
        self.meeting.sitzungsleitung = self.logged_in_user
        self.meeting.save()
        self.check_response_with_user(self.logged_in_user,
            self.logged_in_sitzungsleitung)

    def test_logged_in_protokollant(self):
        if self.logged_in_protokollant is None:
            return
        self.prepare_variables()
        self.meeting.protokollant = self.logged_in_user
        self.meeting.save()
        self.check_response_with_user(self.logged_in_user,
            self.logged_in_protokollant)

    def test_admin_public(self):
        if self.admin_public is None:
            return
        self.prepare_variables()
        self.mt.public = True
        self.mt.save()
        self.check_response_with_user(self.admin_user,
            self.admin_public)

    def test_admin_not_public(self):
        if self.admin_not_public is None:
            return
        self.prepare_variables()
        self.check_response_with_user(self.admin_user,
            self.admin_not_public)
