import pytest
from mixer.backend.django import mixer

from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied

from ..models import MeetingType

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


class AbstractTestView:
    def setup_method(self):
        self.anonymous = None
        self.logged_in = None
        self.staff = None
        self.superuser = None
        self.args = []
        self.redirect_url = None

    def check_response_with_user(self, user, check_result):
        url = self.url.format(*self.args)
        if self.redirect_url is not None:
            redirect_url = self.redirect_url.format(*self.args)
        else:
            redirect_url = None
        req = RequestFactory().get(self.url)
        req.user = user
        check_result(url, redirect_url, self.view, req, *self.args)

    def test_anonymous(self):
        if self.anonymous is None:
            return
        user = AnonymousUser()
        self.check_response_with_user(user, self.anonymous)

    def test_logged_in(self):
        if self.logged_in is None:
            return
        user = mixer.blend('auth.User', is_registered_user=True,
                is_staff=False, is_superuser=False)
        self.check_response_with_user(user, self.logged_in)

    def test_staff(self):
        if self.staff is None:
            return
        user = mixer.blend('auth.User', is_registered_user=True,
                is_staff=True, is_superuser=False)
        self.check_response_with_user(user, self.staff)

    def test_superuser(self):
        if self.superuser is None:
            return
        user = mixer.blend('auth.User', is_registered_user=True,
                is_superuser=True)
        self.check_response_with_user(user, self.superuser)


@pytest.mark.django_db
class AbstractTestMTView:
    def setup_method(self):
        self.anonymous_public = None
        self.anonymous_not_public = None
        self.logged_in_public = None
        self.logged_in_with_rights = None
        self.logged_in_with_admin_rights = None
        self.logged_in_without_rights = None
        self.admin_public = None
        self.admin_not_public = None
        self.args = []
        self.redirect_url = None

    @pytest.fixture(autouse=True)
    def prepare_variables(self):
        self.obj = mixer.blend(MeetingType, pk="abc", id="abc",
            public=False)
        content_type = ContentType.objects.get_for_model(MeetingType)
        self.permission = Permission.objects.get_or_create(codename=self.obj.pk,
            content_type=content_type)[0]
        self.admin_permission = Permission.objects.get_or_create(
            codename=self.obj.pk + MeetingType.ADMIN,
            content_type=content_type)[0]
        self.anonymous_user = AnonymousUser()
        self.logged_in_user = mixer.blend('auth.User',
                is_registered_user=True, is_superuser=False)
        self.admin_user = mixer.blend('auth.User',
                is_registered_user=True, is_superuser=True)

    def check_response_with_user(self, user, check_result):
        args = [self.obj.pk] + self.args
        url = self.url.format(*args)
        if self.redirect_url is not None:
            redirect_url = self.redirect_url.format(*args)
        else:
            redirect_url = None
        req = RequestFactory().get(url)
        req.user = user
        check_result(url, redirect_url, self.view, req, *args)

    def test_anonymous_public(self):
        if self.anonymous_public is None:
            return
        self.prepare_variables()
        self.obj.public = True
        self.obj.save()
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
        self.obj.public = True
        self.obj.save()
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

    def test_admin_public(self):
        if self.admin_public is None:
            return
        self.prepare_variables()
        self.obj.public = True
        self.obj.save()
        self.check_response_with_user(self.admin_user,
            self.admin_public)

    def test_admin_not_public(self):
        if self.admin_not_public is None:
            return
        self.prepare_variables()
        self.check_response_with_user(self.admin_user,
            self.admin_not_public)
