import datetime

from django.utils import timezone

from .access import *
from toptool_common.views import next_view
from .. import views


class TestAddView(AbstractTestMTView):
    def setup_method(self):
        super(TestAddView, self).setup_method()
        self.url = '/{}/add/'
        self.view = views.add
        self.use_meeting = False

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = accessible
        self.logged_in_without_rights = permission_denied
        self.admin_public = accessible
        self.admin_not_public = accessible


class TestAddSeriesView(AbstractTestMTView):
    def setup_method(self):
        super(TestAddSeriesView, self).setup_method()
        self.url = '/{}/addseries/'
        self.view = views.add_series
        self.use_meeting = False

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = accessible
        self.logged_in_without_rights = permission_denied
        self.admin_public = accessible
        self.admin_not_public = accessible


class TestNextMeetingView(AbstractTestMTView):
    def setup_method(self):
        super(TestNextMeetingView, self).setup_method()
        self.url = '/{}/next/'
        self.view = next_view("viewmeeting")
        self.use_meeting = False
        self.use_meeting_for_redirect = True
        self.redirect_url = '/{}/{}/'

        self.anonymous_public = redirect_to_url
        self.anonymous_not_public = redirect_to_url # TODO redirect_to_login
        self.logged_in_public = redirect_to_url
        self.logged_in_with_rights = redirect_to_url
        self.logged_in_with_admin_rights = redirect_to_url # TODO permission_denied
        self.logged_in_without_rights = redirect_to_url # TODO permission_denied
        self.admin_public = redirect_to_url
        self.admin_not_public = redirect_to_url

    def prepare_variables(self):
        super(TestNextMeetingView, self).prepare_variables()
        self.meeting.meetingtype = self.mt
        self.meeting.time = timezone.now() + datetime.timedelta(days=1)
        self.meeting.save()


class TestNoNextMeetingView(AbstractTestMTView):
    def setup_method(self):
        super(TestNoNextMeetingView, self).setup_method()
        self.url = '/{}/next/'
        self.view = next_view("viewmeeting")
        self.use_meeting = False
        self.redirect_url = '/{}/'

        self.anonymous_public = redirect_to_url
        self.anonymous_not_public = redirect_to_url # TODO redirect_to_login
        self.logged_in_public = redirect_to_url
        self.logged_in_with_rights = redirect_to_url
        self.logged_in_with_admin_rights = redirect_to_url # TODO permission_denied
        self.logged_in_without_rights = redirect_to_url # TODO permission_denied
        self.admin_public = redirect_to_url
        self.admin_not_public = redirect_to_url

    def prepare_variables(self):
        super(TestNoNextMeetingView, self).prepare_variables()
        self.meeting.time = timezone.now() - datetime.timedelta(days=1)
        self.meeting.save()


class TestViewMeetingView(AbstractTestMTView):
    def setup_method(self):
        super(TestViewMeetingView, self).setup_method()
        self.url = '/{}/{}/'
        self.view = views.view

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


class TestViewMeetingWrongMTView(AbstractTestMTView):
    def setup_method(self):
        super(TestViewMeetingWrongMTView, self).setup_method()
        self.url = '/{}/{}/'
        self.view = views.view

        self.anonymous_public = redirect_to_login # TODO not_found
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied # TODO not_found
        self.logged_in_with_rights = permission_denied # TODO not_found
        self.logged_in_with_admin_rights = permission_denied
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied
        self.logged_in_protokollant = permission_denied
        self.admin_public = accessible # TODO not_found
        self.admin_not_public = accessible # TODO not_found

    def prepare_variables(self):
        super(TestViewMeetingWrongMTView, self).prepare_variables()
        self.meeting.meetingtype = self.mt2
        self.meeting.save()


class TestEditMeetingView(AbstractTestMTView):
    def setup_method(self):
        super(TestEditMeetingView, self).setup_method()
        self.url = '/{}/{}/edit/'
        self.view = views.edit

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


class TestEditMeetingWrongMTView(AbstractTestMTView):
    def setup_method(self):
        super(TestEditMeetingWrongMTView, self).setup_method()
        self.url = '/{}/{}/edit/'
        self.view = views.edit

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = accessible # TODO not_found
        self.logged_in_protokollant = permission_denied
        self.admin_public = accessible # TODO not_found
        self.admin_not_public = accessible # TODO not_found

    def prepare_variables(self):
        super(TestEditMeetingWrongMTView, self).prepare_variables()
        self.meeting.meetingtype = self.mt2
        self.meeting.save()


class TestDeleteMeetingView(AbstractTestMTView):
    def setup_method(self):
        super(TestDeleteMeetingView, self).setup_method()
        self.url = '/{}/{}/del/'
        self.view = views.delete

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


class TestDeleteMeetingWrongMTView(AbstractTestMTView):
    def setup_method(self):
        super(TestDeleteMeetingWrongMTView, self).setup_method()
        self.url = '/{}/{}/del/'
        self.view = views.delete

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied
        self.logged_in_protokollant = permission_denied
        self.admin_public = accessible # TODO not_found
        self.admin_not_public = accessible # TODO not_found

    def prepare_variables(self):
        super(TestDeleteMeetingWrongMTView, self).prepare_variables()
        self.meeting.meetingtype = self.mt2
        self.meeting.save()


class TestSendTOPsView(AbstractTestMTView):
    def setup_method(self):
        super(TestSendTOPsView, self).setup_method()
        self.url = '/{}/{}/sendtops/'
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


class TestSendTOPsWrongMTView(AbstractTestMTView):
    def setup_method(self):
        super(TestSendTOPsWrongMTView, self).setup_method()
        self.url = '/{}/{}/sendtops/'
        self.view = views.send_tops

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = accessible # TODO not_found
        self.logged_in_protokollant = permission_denied
        self.admin_public = accessible # TODO not_found
        self.admin_not_public = accessible # TODO not_found

    def prepare_variables(self):
        super(TestSendTOPsWrongMTView, self).prepare_variables()
        self.meeting.meetingtype = self.mt2
        self.meeting.save()


class TestSendInvitationView(TestSendTOPsView):
    def setup_method(self):
        super(TestSendInvitationView, self).setup_method()
        self.url = '/{}/{}/sendinvitation/'
        self.view = views.send_invitation


class TestSendInvitationWrongMTView(TestSendTOPsWrongMTView):
    def setup_method(self):
        super(TestSendInvitationWrongMTView, self).setup_method()
        self.url = '/{}/{}/sendinvitation/'
        self.view = views.send_invitation
