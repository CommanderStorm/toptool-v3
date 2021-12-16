# F405
import datetime

from django.utils import timezone

from toptool.tests.test_access_views import (
    AbstractTestImportedView,
    AbstractTestView,
    AbstractTestWrongMTView,
    accessible,
    bad_request,
    not_found,
    permission_denied,
    redirect_to_login,
    redirect_to_url,
)
from toptool.views import next_view

from .. import views

# pylint: disable=too-many-instance-attributes
# pylint: disable=attribute-defined-outside-init


class TestEditTOPsView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/{}/tops/"
        self.view = views.edit_tops

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
        super().setup_method()
        self.url = "/{}/tops/sort/"
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
        super().setup_method()
        self.url = "/{}/nonext/"
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
        super().setup_method()
        self.url = "/{}/listtops/"
        self.view = views.list_tops

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
        super().setup_method()
        self.url = "/{}/next/listtops/"
        self.view = next_view("listtops")
        self.use_meeting = False
        self.use_meeting_for_redirect = True
        self.redirect_url = "/{}/listtops/"

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
        super().prepare_variables()
        self.meeting.time = timezone.now() + datetime.timedelta(days=1)
        self.meeting.save()


class TestNoNextListTOPsView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/{}/next/listtops/"
        self.view = next_view("listtops")
        self.use_meeting = False
        self.redirect_url = "/{}/nonext/"

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
        super().prepare_variables()
        self.meeting.time = timezone.now() - datetime.timedelta(days=1)
        self.meeting.save()


class TestAddTOPView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/{}/addtop/"
        self.view = views.add_top

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
        super().setup_method()
        self.url = "/{}/next/addtop/"
        self.view = next_view("addtop")
        self.use_meeting = False
        self.use_meeting_for_redirect = True
        self.redirect_url = "/{}/addtop/"

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
        super().prepare_variables()
        self.meeting.time = timezone.now() + datetime.timedelta(days=1)
        self.meeting.save()


class TestNoNextAddTOPView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/{}/next/addtop/"
        self.view = next_view("addtop")
        self.use_meeting = False
        self.redirect_url = "/{}/nonext/"

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
        super().prepare_variables()
        self.meeting.time = timezone.now() - datetime.timedelta(days=1)
        self.meeting.save()


class TestEditTOPView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/{}/edittop/{}/"
        self.view = views.edit_top
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
        super().setup_method()
        self.url = "/{}/deltop/{}/"
        self.view = views.delete_top
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
        super().setup_method()
        self.url = "/{}/topattachment/{}/"
        self.view = views.show_attachment
        self.use_top = True

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

    def prepare_variables(self):
        super().prepare_variables()
        self.mt1.attachment_tops = True
        self.mt1.save()


class TestShowTOPAttachmentNotAllowedView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/{}/topattachment/{}/"
        self.view = views.show_attachment
        self.use_top = True

        self.anonymous_public = not_found
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = not_found
        self.logged_in_with_rights = not_found
        self.logged_in_with_admin_rights = permission_denied
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied
        self.logged_in_protokollant = permission_denied
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.mt1.attachment_tops = False
        self.mt1.save()


class TestListSTOPsView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/{}/stdtops/"
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
        super().setup_method()
        self.url = "/{}/stdtops/sort/"
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
        super().setup_method()
        self.url = "/{}/addstdtop/"
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
        super().setup_method()
        self.url = "/{}/editstdtop/{}/"
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
        super().setup_method()
        self.url = "/{}/delstdtop/{}/"
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


class TestEditTOPsWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = "/{}/tops/"
        self.view = views.edit_tops

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


class TestSortTOPsWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = "/{}/tops/sort/"
        self.view = views.sort_tops

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied  # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = bad_request  # TODO not_found
        self.logged_in_protokollant = permission_denied
        self.admin_public = bad_request  # TODO not_found
        self.admin_not_public = bad_request  # TODO not_found


class TestListTOPsWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = "/{}/listtops/"
        self.view = views.list_tops

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


class TestAddTOPWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = "/{}/addtop/"
        self.view = views.add_top

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


class TestEditTOPWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = "/{}/edittop/{}/"
        self.view = views.edit_top
        self.use_top = True

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


class TestDeleteTOPWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = "/{}/deltop/{}/"
        self.view = views.delete_top
        self.use_top = True

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


class TestShowTOPAttachmentWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = "/{}/topattachment/{}/"
        self.view = views.show_attachment
        self.use_top = True

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied  # TODO not_found
        self.logged_in_with_rights = permission_denied  # TODO not_found
        self.logged_in_with_admin_rights = permission_denied
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied
        self.logged_in_protokollant = permission_denied
        self.admin_public = accessible  # TODO not_found
        self.admin_not_public = accessible  # TODO not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.mt2.attachment_tops = True
        self.mt2.save()


class TestShowTOPAttachmentNotAllowedWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = "/{}/topattachment/{}/"
        self.view = views.show_attachment
        self.use_top = True

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied  # TODO not_found
        self.logged_in_with_rights = permission_denied  # TODO not_found
        self.logged_in_with_admin_rights = permission_denied
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied
        self.logged_in_protokollant = permission_denied
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.mt2.attachment_tops = False
        self.mt2.save()


class TestEditTOPsImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = "/{}/tops/"
        self.view = views.edit_tops

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


class TestSortTOPsImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = "/{}/tops/sort/"
        self.view = views.sort_tops

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


class TestListTOPsImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = "/{}/listtops/"
        self.view = views.list_tops

        self.anonymous_public = permission_denied
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied
        self.logged_in_protokollant = permission_denied
        self.admin_public = permission_denied
        self.admin_not_public = permission_denied


class TestAddTOPImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = "/{}/addtop/"
        self.view = views.add_top

        self.anonymous_public = permission_denied
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied
        self.logged_in_protokollant = permission_denied
        self.admin_public = permission_denied
        self.admin_not_public = permission_denied


class TestEditTOPImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = "/{}/edittop/{}/"
        self.view = views.edit_top
        self.use_top = True

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


class TestDeleteTOPImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = "/{}/deltop/{}/"
        self.view = views.delete_top
        self.use_top = True

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


class TestShowTOPAttachmentImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = "/{}/topattachment/{}/"
        self.view = views.show_attachment
        self.use_top = True

        self.anonymous_public = permission_denied
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied
        self.logged_in_protokollant = permission_denied
        self.admin_public = permission_denied
        self.admin_not_public = permission_denied

    def prepare_variables(self):
        super().prepare_variables()
        self.mt1.attachment_tops = True
        self.mt1.save()


class TestShowTOPAttachmentNotAllowedImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = "/{}/topattachment/{}/"
        self.view = views.show_attachment
        self.use_top = True

        self.anonymous_public = permission_denied
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied
        self.logged_in_protokollant = permission_denied
        self.admin_public = permission_denied
        self.admin_not_public = permission_denied

    def prepare_variables(self):
        super().prepare_variables()
        self.mt1.attachment_tops = False
        self.mt1.save()
