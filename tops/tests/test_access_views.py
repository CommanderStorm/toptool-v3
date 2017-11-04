import datetime

from django.utils import timezone

from toptool.tests.access import *
from toptool_common.views import next_view
from .. import views


class TestEditTOPsView(AbstractTestView):
    def setup_method(self):
        super(TestEditTOPsView, self).setup_method()
        self.url = '/{}/{}/tops/'
        self.view = views.tops

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


class TestSortTOPsView(AbstractTestView):
    def setup_method(self):
        super(TestSortTOPsView, self).setup_method()
        self.url = '/{}/{}/tops/sort/'
        self.view = views.sort_tops

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = bad_request
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = bad_request
        self.logged_in_protokollant = permission_denied
        self.admin_public = bad_request
        self.admin_not_public = bad_request


class TestNoNextView(AbstractTestView):
    def setup_method(self):
        super(TestNoNextView, self).setup_method()
        self.url = '/{}/nonext/'
        self.view = views.nonext
        self.use_meeting = False

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


class TestListTOPsView(AbstractTestView):
    def setup_method(self):
        super(TestListTOPsView, self).setup_method()
        self.url = '/{}/{}/listtops/'
        self.view = views.list

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


class TestNextListTOPsView(AbstractTestView):
    def setup_method(self):
        super(TestNextListTOPsView, self).setup_method()
        self.url = '/{}/next/listtops/'
        self.view = next_view("listtops")
        self.use_meeting = False
        self.use_meeting_for_redirect = True
        self.redirect_url = '/{}/{}/listtops/'

        self.anonymous_public = redirect_to_url
        self.anonymous_not_public = redirect_to_url # TODO redirect_to_login
        self.logged_in_public = redirect_to_url
        self.logged_in_with_rights = redirect_to_url
        self.logged_in_with_admin_rights = redirect_to_url # TODO permission_denied
        self.logged_in_without_rights = redirect_to_url # TODO permission_denied
        self.logged_in_sitzungsleitung = redirect_to_url # TODO permission_denied
        self.logged_in_protokollant = redirect_to_url # TODO permission_denied
        self.admin_public = redirect_to_url
        self.admin_not_public = redirect_to_url

    def prepare_variables(self):
        super(TestNextListTOPsView, self).prepare_variables()
        self.meeting.time = timezone.now() + datetime.timedelta(days=1)
        self.meeting.save()


class TestNoNextListTOPsView(AbstractTestView):
    def setup_method(self):
        super(TestNoNextListTOPsView, self).setup_method()
        self.url = '/{}/next/listtops/'
        self.view = next_view("listtops")
        self.use_meeting = False
        self.redirect_url = '/{}/nonext/'

        self.anonymous_public = redirect_to_url
        self.anonymous_not_public = redirect_to_url # TODO redirect_to_login
        self.logged_in_public = redirect_to_url
        self.logged_in_with_rights = redirect_to_url
        self.logged_in_with_admin_rights = redirect_to_url # TODO permission_denied
        self.logged_in_without_rights = redirect_to_url # TODO permission_denied
        self.logged_in_sitzungsleitung = redirect_to_url # TODO permission_denied
        self.logged_in_protokollant = redirect_to_url # TODO permission_denied
        self.admin_public = redirect_to_url
        self.admin_not_public = redirect_to_url

    def prepare_variables(self):
        super(TestNoNextListTOPsView, self).prepare_variables()
        self.meeting.time = timezone.now() - datetime.timedelta(days=1)
        self.meeting.save()


class TestAddTOPView(AbstractTestView):
    def setup_method(self):
        super(TestAddTOPView, self).setup_method()
        self.url = '/{}/{}/addtop/'
        self.view = views.add

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


class TestNextAddTOPView(AbstractTestView):
    def setup_method(self):
        super(TestNextAddTOPView, self).setup_method()
        self.url = '/{}/next/addtop/'
        self.view = next_view("addtop")
        self.use_meeting = False
        self.use_meeting_for_redirect = True
        self.redirect_url = '/{}/{}/addtop/'

        self.anonymous_public = redirect_to_url
        self.anonymous_not_public = redirect_to_url # TODO redirect_to_login
        self.logged_in_public = redirect_to_url
        self.logged_in_with_rights = redirect_to_url
        self.logged_in_with_admin_rights = redirect_to_url # TODO permission_denied
        self.logged_in_without_rights = redirect_to_url # TODO permission_denied
        self.logged_in_sitzungsleitung = redirect_to_url # TODO permission_denied
        self.logged_in_protokollant = redirect_to_url # TODO permission_denied
        self.admin_public = redirect_to_url
        self.admin_not_public = redirect_to_url

    def prepare_variables(self):
        super(TestNextAddTOPView, self).prepare_variables()
        self.meeting.time = timezone.now() + datetime.timedelta(days=1)
        self.meeting.save()


class TestNoNextAddTOPView(AbstractTestView):
    def setup_method(self):
        super(TestNoNextAddTOPView, self).setup_method()
        self.url = '/{}/next/addtop/'
        self.view = next_view("addtop")
        self.use_meeting = False
        self.redirect_url = '/{}/nonext/'

        self.anonymous_public = redirect_to_url
        self.anonymous_not_public = redirect_to_url # TODO redirect_to_login
        self.logged_in_public = redirect_to_url
        self.logged_in_with_rights = redirect_to_url
        self.logged_in_with_admin_rights = redirect_to_url # TODO permission_denied
        self.logged_in_without_rights = redirect_to_url # TODO permission_denied
        self.logged_in_sitzungsleitung = redirect_to_url # TODO permission_denied
        self.logged_in_protokollant = redirect_to_url # TODO permission_denied
        self.admin_public = redirect_to_url
        self.admin_not_public = redirect_to_url

    def prepare_variables(self):
        super(TestNoNextAddTOPView, self).prepare_variables()
        self.meeting.time = timezone.now() - datetime.timedelta(days=1)
        self.meeting.save()


class TestEditTOPView(AbstractTestView):
    def setup_method(self):
        super(TestEditTOPView, self).setup_method()
        self.url = '/{}/{}/edittop/{}/'
        self.view = views.edit
        self.use_top = True

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


class TestDeleteTOPView(AbstractTestView):
    def setup_method(self):
        super(TestDeleteTOPView, self).setup_method()
        self.url = '/{}/{}/deltop/{}/'
        self.view = views.delete
        self.use_top = True

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


class TestShowTOPAttachmentView(AbstractTestView):
    def setup_method(self):
        super(TestShowTOPAttachmentView, self).setup_method()
        self.url = '/{}/{}/topattachment/{}/'
        self.view = views.show_attachment
        self.use_top = True

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied # TODO accessible
        self.logged_in_with_rights = accessible
        self.logged_in_with_admin_rights = permission_denied
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied
        self.logged_in_protokollant = permission_denied
        self.admin_public = accessible
        self.admin_not_public = accessible

    def prepare_variables(self):
        super(TestShowTOPAttachmentView, self).prepare_variables()
        self.mt.attachment_tops = True
        self.mt.save()


class TestShowTOPAttachmentNotAllowedView(AbstractTestView):
    def setup_method(self):
        super(TestShowTOPAttachmentNotAllowedView, self).setup_method()
        self.url = '/{}/{}/topattachment/{}/'
        self.view = views.show_attachment
        self.use_top = True

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied # TODO not_found
        self.logged_in_with_rights = not_found
        self.logged_in_with_admin_rights = permission_denied
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied
        self.logged_in_protokollant = permission_denied
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super(TestShowTOPAttachmentNotAllowedView, self).prepare_variables()
        self.mt.attachment_tops = False
        self.mt.save()


class TestListSTOPsView(AbstractTestView):
    def setup_method(self):
        super(TestListSTOPsView, self).setup_method()
        self.url = '/{}/stdtops/'
        self.view = views.stdtops
        self.use_meeting = False

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = accessible
        self.logged_in_without_rights = permission_denied
        self.admin_public = accessible
        self.admin_not_public = accessible


class TestSortSTOPsView(AbstractTestView):
    def setup_method(self):
        super(TestSortSTOPsView, self).setup_method()
        self.url = '/{}/stdtops/sort/'
        self.view = views.sort_stdtops
        self.use_meeting = False

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = bad_request
        self.logged_in_without_rights = permission_denied
        self.admin_public = bad_request
        self.admin_not_public = bad_request


class TestAddSTOPsView(AbstractTestView):
    def setup_method(self):
        super(TestAddSTOPsView, self).setup_method()
        self.url = '/{}/addstdtop/'
        self.view = views.add_std
        self.use_meeting = False

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = accessible
        self.logged_in_without_rights = permission_denied
        self.admin_public = accessible
        self.admin_not_public = accessible


class TestEditSTOPsView(AbstractTestView):
    def setup_method(self):
        super(TestEditSTOPsView, self).setup_method()
        self.url = '/{}/editstdtop/{}/'
        self.view = views.edit_std
        self.use_std_top = True

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = accessible
        self.logged_in_without_rights = permission_denied
        self.admin_public = accessible
        self.admin_not_public = accessible


class TestDeleteSTOPsView(AbstractTestView):
    def setup_method(self):
        super(TestDeleteSTOPsView, self).setup_method()
        self.url = '/{}/delstdtop/{}/'
        self.view = views.delete_std
        self.use_std_top = True

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = accessible
        self.logged_in_without_rights = permission_denied
        self.admin_public = accessible
        self.admin_not_public = accessible
