import datetime

from django.utils import timezone

from toptool.tests.test_access_views import (
    AbstractTestImportedView,
    AbstractTestView,
    AbstractTestWrongMTView,
    accessible,
    permission_denied,
    redirect_to_login,
    redirect_to_url,
)
from toptool.views import next_view

from .. import views

# pylint: disable=too-many-instance-attributes
# pylint: disable=attribute-defined-outside-init
# pylint: disable=super-with-arguments


class TestAddView(AbstractTestView):
    def setup_method(self):
        super(TestAddView, self).setup_method()
        self.url = "/meeting/add/{}/"
        self.view = views.add_meeting
        self.use_meeting = False

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = accessible
        self.logged_in_without_rights = permission_denied
        self.admin_public = accessible
        self.admin_not_public = accessible


class TestAddSeriesView(AbstractTestView):
    def setup_method(self):
        super(TestAddSeriesView, self).setup_method()
        self.url = "/meeting/add/series/{}/"
        self.view = views.add_meetings_series
        self.use_meeting = False

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = accessible
        self.logged_in_without_rights = permission_denied
        self.admin_public = accessible
        self.admin_not_public = accessible


class TestNextMeetingView(AbstractTestView):
    def setup_method(self):
        super(TestNextMeetingView, self).setup_method()
        self.url = "/{}/next/"
        self.view = next_view("meetings:view_meeting")
        self.use_meeting = False
        self.use_meeting_for_redirect = True
        self.redirect_url = "/meeting/{}/"

        self.anonymous_public = redirect_to_url
        self.anonymous_not_public = redirect_to_url  # TODO redirect_to_login
        self.logged_in_public = redirect_to_url
        self.logged_in_with_rights = redirect_to_url
        self.logged_in_with_admin_rights = redirect_to_url  # TODO permission_denied
        self.logged_in_without_rights = redirect_to_url  # TODO permission_denied
        self.logged_in_sitzungsleitung = redirect_to_url  # TODO permission_denied
        self.logged_in_protokollant = redirect_to_url  # TODO permission_denied
        self.admin_public = redirect_to_url
        self.admin_not_public = redirect_to_url

    def prepare_variables(self):
        super(TestNextMeetingView, self).prepare_variables()
        self.meeting.meetingtype = self.mt1
        self.meeting.time = timezone.now() + datetime.timedelta(days=1)
        self.meeting.save()


class TestNoNextMeetingView(AbstractTestView):
    def setup_method(self):
        super(TestNoNextMeetingView, self).setup_method()
        self.url = "/{}/next/"
        self.view = next_view("meetings:view_meeting")
        self.use_meeting = False
        self.redirect_url = "/meeting/{}/"

        self.anonymous_public = redirect_to_url
        self.anonymous_not_public = redirect_to_url  # TODO redirect_to_login
        self.logged_in_public = redirect_to_url
        self.logged_in_with_rights = redirect_to_url
        self.logged_in_with_admin_rights = redirect_to_url  # TODO permission_denied
        self.logged_in_without_rights = redirect_to_url  # TODO permission_denied
        self.logged_in_sitzungsleitung = redirect_to_url  # TODO permission_denied
        self.logged_in_protokollant = redirect_to_url  # TODO permission_denied
        self.admin_public = redirect_to_url
        self.admin_not_public = redirect_to_url

    def prepare_variables(self):
        super(TestNoNextMeetingView, self).prepare_variables()
        self.meeting.time = timezone.now() - datetime.timedelta(days=1)
        self.meeting.save()


class TestViewMeetingView(AbstractTestView):
    def setup_method(self):
        super(TestViewMeetingView, self).setup_method()
        self.url = "/meeting/{}/"
        self.view = views.view_meeting

        self.anonymous_public = accessible
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = accessible
        self.logged_in_with_rights = accessible
        self.logged_in_with_admin_rights = permission_denied
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied
        self.logged_in_protokollant = permission_denied
        self.admin_public = accessible
        self.admin_not_public = accessible


class TestViewMeetingWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super(TestViewMeetingWrongMTView, self).setup_method()
        self.url = "/meeting/{}/"
        self.view = views.view_meeting

        self.anonymous_public = redirect_to_login  # TODO not_found
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied  # TODO not_found
        self.logged_in_with_rights = permission_denied  # TODO not_found
        self.logged_in_with_admin_rights = permission_denied
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied
        self.logged_in_protokollant = permission_denied
        self.admin_public = accessible  # TODO not_found
        self.admin_not_public = accessible  # TODO not_found


class TestEditMeetingView(AbstractTestView):
    def setup_method(self):
        super(TestEditMeetingView, self).setup_method()
        self.url = "/meeting/{}/edit/"
        self.view = views.edit_meeting

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = accessible
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = accessible
        self.logged_in_protokollant = permission_denied
        self.admin_public = accessible
        self.admin_not_public = accessible


class TestEditMeetingWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super(TestEditMeetingWrongMTView, self).setup_method()
        self.url = "/meeting/{}/edit/"
        self.view = views.edit_meeting

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied  # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = accessible  # TODO not_found
        self.logged_in_protokollant = permission_denied
        self.admin_public = accessible  # TODO not_found
        self.admin_not_public = accessible  # TODO not_found


class TestDeleteMeetingView(AbstractTestView):
    def setup_method(self):
        super(TestDeleteMeetingView, self).setup_method()
        self.url = "/meeting/{}/delete/"
        self.view = views.del_meeting

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = accessible
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied
        self.logged_in_protokollant = permission_denied
        self.admin_public = accessible
        self.admin_not_public = accessible


class TestDeleteMeetingWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super(TestDeleteMeetingWrongMTView, self).setup_method()
        self.url = "/meeting/{}/delete/"
        self.view = views.del_meeting

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied  # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied
        self.logged_in_protokollant = permission_denied
        self.admin_public = accessible  # TODO not_found
        self.admin_not_public = accessible  # TODO not_found


class TestSendTOPsView(AbstractTestView):
    def setup_method(self):
        super(TestSendTOPsView, self).setup_method()
        self.url = "/meeting/{}/sendtops/"
        self.view = views.send_tops

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = accessible
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = accessible
        self.logged_in_protokollant = permission_denied
        self.admin_public = accessible
        self.admin_not_public = accessible


class TestSendTOPsWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super(TestSendTOPsWrongMTView, self).setup_method()
        self.url = "/meeting/{}/sendtops/"
        self.view = views.send_tops

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied  # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = accessible  # TODO not_found
        self.logged_in_protokollant = permission_denied
        self.admin_public = accessible  # TODO not_found
        self.admin_not_public = accessible  # TODO not_found


class TestSendInvitationView(TestSendTOPsView):
    def setup_method(self):
        super(TestSendInvitationView, self).setup_method()
        self.url = "/meeting/{}/sendinvitation/"
        self.view = views.send_invitation


class TestSendInvitationWrongMTView(TestSendTOPsWrongMTView):
    def setup_method(self):
        super(TestSendInvitationWrongMTView, self).setup_method()
        self.url = "/meeting/{}/sendinvitation/"
        self.view = views.send_invitation


class TestSendTOPsImportedView(AbstractTestImportedView):
    def setup_method(self):
        super(TestSendTOPsImportedView, self).setup_method()
        self.url = "/meeting/{}/sendtops/"
        self.view = views.send_tops

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied
        self.logged_in_protokollant = permission_denied
        self.admin_public = permission_denied
        self.admin_not_public = permission_denied


class TestSendInvitationImportedView(TestSendTOPsImportedView):
    def setup_method(self):
        super(TestSendInvitationImportedView, self).setup_method()
        self.url = "/meeting/{}/sendinvitation/"
        self.view = views.send_invitation
