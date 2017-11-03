from .access import *
from .. import views, feeds


class TestOwnMTsView(AbstractTestView):
    def setup_method(self):
        super(TestOwnMTsView, self).setup_method()
        self.url = '/overview'
        self.view = views.index

        self.anonymous = redirect_to_login
        self.logged_in = accessible
        self.staff = accessible
        self.superuser = accessible


class TestAllMTsView(AbstractTestView):
    def setup_method(self):
        super(TestAllMTsView, self).setup_method()
        self.url = '/all'
        self.view = views.index_all

        self.anonymous = redirect_to_login
        self.logged_in = redirect_to_login # TODO permission_denied
        self.staff = accessible # TODO permission_denied
        self.superuser = redirect_to_login # TODO accessible


class TestAddMTView (AbstractTestView):
    def setup_method(self):
        super(TestAddMTView, self).setup_method()
        self.url = '/add'
        self.view = views.add

        self.anonymous = redirect_to_login
        self.logged_in = redirect_to_login # TODO permission_denied
        self.staff = accessible # TODO permission_denied
        self.superuser = redirect_to_login # TODO accessible


class TestViewMTView (AbstractTestMTView):
    def setup_method(self):
        super(TestViewMTView, self).setup_method()
        self.url = '/{}/'
        self.view = views.view

        self.anonymous_public = accessible
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = accessible
        self.logged_in_with_rights = accessible
        self.logged_in_with_admin_rights = permission_denied # TODO accessible
        self.logged_in_without_rights = permission_denied
        self.admin_public = accessible
        self.admin_not_public = accessible


class TestEditMTView (AbstractTestMTView):
    def setup_method(self):
        super(TestEditMTView, self).setup_method()
        self.url = '/{}/edit/'
        self.view = views.edit

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = accessible
        self.logged_in_without_rights = permission_denied
        self.admin_public = accessible
        self.admin_not_public = accessible


class TestDeleteMTView (AbstractTestMTView):
    def setup_method(self):
        super(TestDeleteMTView, self).setup_method()
        self.url = '/{}/del/'
        self.view = views.delete

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = redirect_to_login # TODO permission_denied
        self.logged_in_with_rights = redirect_to_login # TODO permission_denied
        self.logged_in_with_admin_rights = redirect_to_login # TODO permission_denied
        self.logged_in_without_rights = redirect_to_login # TODO permission_denied
        self.admin_public = redirect_to_login # TODO accessible
        self.admin_not_public = redirect_to_login # TODO accessible


class TestUpcomingMTView (AbstractTestMTView):
    def setup_method(self):
        super(TestUpcomingMTView, self).setup_method()
        self.url = '/{}/upcoming/'
        self.view = views.upcoming

        self.anonymous_public = accessible
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = accessible
        self.logged_in_with_rights = accessible
        self.logged_in_with_admin_rights = permission_denied # TODO accessible
        self.logged_in_without_rights = permission_denied
        self.admin_public = accessible
        self.admin_not_public = accessible


class TestIcalMTView (AbstractTestMTView):
    def setup_method(self):
        super(TestIcalMTView, self).setup_method()
        self.url = '/{}/ical/'
        self.view = feeds.MeetingFeed()

        self.anonymous_public = accessible
        self.anonymous_not_public = permission_denied
        self.logged_in_public = accessible
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied # TODO accessible
        self.logged_in_without_rights = permission_denied
        self.admin_public = accessible
        self.admin_not_public = permission_denied


class TestViewArchiveMTView (AbstractTestMTView):
    def setup_method(self):
        super(TestViewArchiveMTView, self).setup_method()
        self.url = '/{}/archive/'
        self.view = views.view_archive
        self.args = ["2011"]
        self.redirect_url = '/{}/'

        self.anonymous_public = redirect_to_url
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = redirect_to_url
        self.logged_in_with_rights = redirect_to_url
        self.logged_in_with_admin_rights = permission_denied # TODO accessible
        self.logged_in_without_rights = permission_denied
        self.admin_public = redirect_to_url
        self.admin_not_public = redirect_to_url
