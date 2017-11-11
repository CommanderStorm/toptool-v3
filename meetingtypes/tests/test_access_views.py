from django.contrib.auth import views as auth_views

from toptool.tests.access import *
from .. import views, feeds


class TestLoginView(AbstractTestView):
    def setup_method(self):
        super(TestLoginView, self).setup_method()
        self.url = '/login/'
        self.view = auth_views.login
        self.use_mt = False
        self.use_meeting = False

        self.anonymous_public = accessible
        self.anonymous_not_public = accessible
        self.logged_in_public = accessible # TODO not_found
        self.logged_in_with_rights = accessible # TODO not_found
        self.logged_in_with_admin_rights = accessible # TODO not_found
        self.logged_in_without_rights = accessible # TODO not_found
        self.admin_public = accessible # TODO not_found
        self.admin_not_public = accessible # TODO not_found


class TestLogoutView(AbstractTestView):
    def setup_method(self):
        super(TestLogoutView, self).setup_method()
        self.url = '/logout/'
        self.view = auth_views.logout
        self.use_mt = False
        self.use_meeting = False
        self.redirect_url = '/'

        self.anonymous_public = error(AttributeError) # TODO redirect_to_login
        self.anonymous_not_public = error(AttributeError) # TODO redirect_to_login
        self.logged_in_public = error(AttributeError)
        self.logged_in_with_rights = error(AttributeError)
        self.logged_in_with_admin_rights = error(AttributeError)
        self.logged_in_without_rights = error(AttributeError)
        self.admin_public = error(AttributeError)
        self.admin_not_public = error(AttributeError)


class TestOwnMTsView(AbstractTestView):
    def setup_method(self):
        super(TestOwnMTsView, self).setup_method()
        self.url = '/overview'
        self.view = views.index
        self.use_mt = False
        self.use_meeting = False

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = accessible
        self.logged_in_with_rights = accessible
        self.logged_in_with_admin_rights = accessible
        self.logged_in_without_rights = accessible
        self.admin_public = accessible
        self.admin_not_public = accessible


class TestAllMTsView(AbstractTestView):
    def setup_method(self):
        super(TestAllMTsView, self).setup_method()
        self.url = '/all'
        self.view = views.index_all
        self.use_mt = False
        self.use_meeting = False

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = redirect_to_login # TODO permission_denied
        self.logged_in_with_rights = redirect_to_login # TODO permission_denied
        self.logged_in_with_admin_rights = redirect_to_login # TODO permission_denied
        self.logged_in_without_rights = redirect_to_login # TODO permission_denied
        self.admin_public = redirect_to_login # TODO accessible
        self.admin_not_public = redirect_to_login # TODO accessible


class TestAddMTView (AbstractTestView):
    def setup_method(self):
        super(TestAddMTView, self).setup_method()
        self.url = '/add'
        self.view = views.add
        self.use_mt = False
        self.use_meeting = False

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = redirect_to_login # TODO permission_denied
        self.logged_in_with_rights = redirect_to_login # TODO permission_denied
        self.logged_in_with_admin_rights = redirect_to_login # TODO permission_denied
        self.logged_in_without_rights = redirect_to_login # TODO permission_denied
        self.admin_public = redirect_to_login # TODO accessible
        self.admin_not_public = redirect_to_login # TODO accessible


class TestViewMTView (AbstractTestView):
    def setup_method(self):
        super(TestViewMTView, self).setup_method()
        self.url = '/{}/'
        self.view = views.view
        self.use_meeting = False

        self.anonymous_public = accessible
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = accessible
        self.logged_in_with_rights = accessible
        self.logged_in_with_admin_rights = permission_denied # TODO accessible
        self.logged_in_without_rights = permission_denied
        self.admin_public = accessible
        self.admin_not_public = accessible


class TestEditMTView (AbstractTestView):
    def setup_method(self):
        super(TestEditMTView, self).setup_method()
        self.url = '/{}/edit/'
        self.view = views.edit
        self.use_meeting = False

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = accessible
        self.logged_in_without_rights = permission_denied
        self.admin_public = accessible
        self.admin_not_public = accessible


class TestDeleteMTView (AbstractTestView):
    def setup_method(self):
        super(TestDeleteMTView, self).setup_method()
        self.url = '/{}/del/'
        self.view = views.delete
        self.use_meeting = False

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = redirect_to_login # TODO permission_denied
        self.logged_in_with_rights = redirect_to_login # TODO permission_denied
        self.logged_in_with_admin_rights = redirect_to_login # TODO permission_denied
        self.logged_in_without_rights = redirect_to_login # TODO permission_denied
        self.admin_public = redirect_to_login # TODO accessible
        self.admin_not_public = redirect_to_login # TODO accessible


class TestUpcomingMTView (AbstractTestView):
    def setup_method(self):
        super(TestUpcomingMTView, self).setup_method()
        self.url = '/{}/upcoming/'
        self.view = views.upcoming
        self.use_meeting = False

        self.anonymous_public = accessible
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = accessible
        self.logged_in_with_rights = accessible
        self.logged_in_with_admin_rights = permission_denied # TODO accessible
        self.logged_in_without_rights = permission_denied
        self.admin_public = accessible
        self.admin_not_public = accessible


class TestIcalMTView (AbstractTestView):
    def setup_method(self):
        super(TestIcalMTView, self).setup_method()
        self.url = '/{}/ical/'
        self.view = feeds.MeetingFeed()
        self.use_meeting = False

        self.anonymous_public = accessible
        self.anonymous_not_public = permission_denied
        self.logged_in_public = accessible
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied # TODO accessible
        self.logged_in_without_rights = permission_denied
        self.admin_public = accessible
        self.admin_not_public = permission_denied


class TestViewArchiveMTView (AbstractTestView):
    def setup_method(self):
        super(TestViewArchiveMTView, self).setup_method()
        self.url = '/{}/archive/{}/'
        self.view = views.view_archive
        self.args = ["2011"]
        self.redirect_url = '/{}/'
        self.use_meeting = False

        self.anonymous_public = accessible
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = accessible
        self.logged_in_with_rights = accessible
        self.logged_in_with_admin_rights = permission_denied
        self.logged_in_without_rights = permission_denied
        self.admin_public = accessible
        self.admin_not_public = accessible

    def prepare_variables(self):
        super(TestViewArchiveMTView, self).prepare_variables()
        self.meeting.time = self.meeting.time.replace(year=2011)
        self.meeting.save()


class TestViewArchiveMTWrongYearView (AbstractTestView):
    def setup_method(self):
        super(TestViewArchiveMTWrongYearView, self).setup_method()
        self.url = '/{}/archive/'
        self.view = views.view_archive
        self.args = ["2011"]
        self.redirect_url = '/{}/'
        self.use_meeting = False

        self.anonymous_public = redirect_to_url
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = redirect_to_url
        self.logged_in_with_rights = redirect_to_url
        self.logged_in_with_admin_rights = permission_denied
        self.logged_in_without_rights = permission_denied
        self.admin_public = redirect_to_url
        self.admin_not_public = redirect_to_url

    def prepare_variables(self):
        super(TestViewArchiveMTWrongYearView, self).prepare_variables()
        self.meeting.time = self.meeting.time.replace(year=2012)
        self.meeting.save()
