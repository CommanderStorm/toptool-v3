from toptool.tests.access import *
from .. import views


class TestShowProtokollView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/{}/'
        self.view = views.show_protokoll
        self.args = [self.filetype]
        self.redirect_url = '/protokolle/{}/{}/{}/'

        self.anonymous_public = redirect_to_url
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
        self.protokoll.approved = True
        self.protokoll.published = True
        self.protokoll.save()


class TestShowProtokollNotApprovedView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/{}/'
        self.view = views.show_protokoll
        self.args = [self.filetype]
        self.redirect_url = '/protokolle/{}/{}/{}/'

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = accessible
        self.logged_in_with_admin_rights = permission_denied
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied
        self.logged_in_protokollant = permission_denied
        self.admin_public = accessible
        self.admin_not_public = accessible

    def prepare_variables(self):
        super().prepare_variables()
        self.protokoll.approved = False
        self.protokoll.published = True
        self.protokoll.save()


class TestShowPublicProtokollView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = '/protokolle/{}/{}/{}/'
        self.view = views.show_public_protokoll
        self.args = [self.filetype]
        self.redirect_url = '/{}/{}/protokoll/{}/'

        self.anonymous_public = accessible
        self.anonymous_not_public = redirect_to_url # TODO redirect_to_login
        self.logged_in_public = accessible # TODO redirect_to_url
        self.logged_in_with_rights = redirect_to_url
        self.logged_in_with_admin_rights = redirect_to_url # TODO permission_denied
        self.logged_in_without_rights = redirect_to_url # TODO permission_denied
        self.logged_in_sitzungsleitung = redirect_to_url # TODO permission_denied
        self.logged_in_protokollant = redirect_to_url # TODO permission_denied
        self.admin_public = accessible # TODO redirect_to_url
        self.admin_not_public = redirect_to_url

    def prepare_variables(self):
        super().prepare_variables()
        self.protokoll.approved = True
        self.protokoll.published = True
        self.protokoll.save()


class TestShowPublicProtokollNotApprovedView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = '/protokolle/{}/{}/{}/'
        self.view = views.show_public_protokoll
        self.args = [self.filetype]
        self.redirect_url = '/{}/{}/protokoll/{}/'

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
        super().prepare_variables()
        self.protokoll.approved = False
        self.protokoll.published = True
        self.protokoll.save()


class TestDownloadTemplatesOtherProtokollantView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/templates/'
        self.view = views.templates

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = accessible
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = accessible
        self.logged_in_protokollant = accessible
        self.admin_public = accessible
        self.admin_not_public = accessible

    def prepare_variables(self):
        super(TestDownloadTemplatesOtherProtokollantView, self).prepare_variables()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestDownloadTemplatesNoProtokollantView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/templates/'
        self.view = views.templates

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = accessible
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = accessible
        self.logged_in_protokollant = accessible
        self.admin_public = accessible
        self.admin_not_public = accessible

    def prepare_variables(self):
        super(TestDownloadTemplatesNoProtokollantView, self).prepare_variables()
        self.meeting.protokollant = None
        self.meeting.save()


class TestEditProtokollOtherProtokollantView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/edit/'
        self.view = views.edit_protokoll

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = accessible
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = accessible
        self.logged_in_protokollant = accessible
        self.admin_public = accessible
        self.admin_not_public = accessible

    def prepare_variables(self):
        super(TestEditProtokollOtherProtokollantView, self).prepare_variables()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestPadOtherProtokollantView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/pad/'
        self.view = views.pad

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = ifthenelse(self.pad_test(), accessible, not_found)
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = ifthenelse(self.pad_test(), accessible, not_found)
        self.logged_in_protokollant = ifthenelse(self.pad_test(), accessible, not_found)
        self.admin_public = ifthenelse(self.pad_test(), accessible, not_found)
        self.admin_not_public = ifthenelse(self.pad_test(), accessible, not_found)

    def prepare_variables(self):
        super(TestPadOtherProtokollantView, self).prepare_variables()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestEditProtokollNoProtokollantView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/edit/'
        self.view = views.edit_protokoll

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = accessible
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = accessible
        self.logged_in_protokollant = accessible
        self.admin_public = accessible
        self.admin_not_public = accessible

    def prepare_variables(self):
        super(TestEditProtokollNoProtokollantView, self).prepare_variables()
        self.meeting.protokollant = None
        self.meeting.save()


class TestPadNoProtokollantView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/pad/'
        self.view = views.pad

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = ifthenelse(self.pad_test(), accessible, not_found)
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = ifthenelse(self.pad_test(), accessible, not_found)
        self.logged_in_protokollant = ifthenelse(self.pad_test(), accessible, not_found)
        self.admin_public = ifthenelse(self.pad_test(), accessible, not_found)
        self.admin_not_public = ifthenelse(self.pad_test(), accessible, not_found)

    def prepare_variables(self):
        super(TestPadNoProtokollantView, self).prepare_variables()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestDelProtokollView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/delete/'
        self.view = views.delete_protokoll

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


class TestProtokollSuccessView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/success/'
        self.view = views.success_protokoll

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = accessible
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = accessible
        self.logged_in_protokollant = accessible
        self.admin_public = accessible
        self.admin_not_public = accessible


class TestSendProtokollView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/send/'
        self.view = views.send_protokoll

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = error(AttributeError) # TODO accessible
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = error(AttributeError) # TODO accessible
        self.logged_in_protokollant = accessible
        self.admin_public = error(AttributeError) # TODO accessible
        self.admin_not_public = error(AttributeError) # TODO accessible

    def prepare_variables(self):
        super().prepare_variables()
        self.protokoll.published = True
        self.protokoll.save()


class TestProtokollAttachmentsAllowedView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/'
        self.view = views.attachments

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = accessible
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = accessible
        self.logged_in_protokollant = accessible
        self.admin_public = accessible
        self.admin_not_public = accessible

    def prepare_variables(self):
        super().prepare_variables()
        self.mt.attachment_protokoll = True
        self.mt.save()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestProtokollAttachmentsNotAllowedView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/'
        self.view = views.attachments

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = not_found
        self.logged_in_protokollant = not_found
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.mt.attachment_protokoll = False
        self.mt.save()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestProtokollAttachmentsAllowedNoProtokollantView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/'
        self.view = views.attachments

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = accessible
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = accessible
        self.logged_in_protokollant = accessible
        self.admin_public = accessible
        self.admin_not_public = accessible

    def prepare_variables(self):
        super().prepare_variables()
        self.mt.attachment_protokoll = True
        self.mt.save()
        self.meeting.protokollant = None
        self.meeting.save()


class TestProtokollAttachmentsNotAllowedNoProtokollantView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/'
        self.view = views.attachments

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = not_found
        self.logged_in_protokollant = not_found
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.mt.attachment_protokoll = False
        self.mt.save()
        self.meeting.protokollant = None
        self.meeting.save()


class TestSortProtokollAttachmentsAllowedView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/sort/'
        self.view = views.sort_attachments

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = bad_request
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = bad_request
        self.logged_in_protokollant = bad_request
        self.admin_public = bad_request
        self.admin_not_public = bad_request

    def prepare_variables(self):
        super().prepare_variables()
        self.mt.attachment_protokoll = True
        self.mt.save()


class TestSortProtokollAttachmentsNotAllowedView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/sort/'
        self.view = views.sort_attachments

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = not_found
        self.logged_in_protokollant = not_found
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.mt.attachment_protokoll = False
        self.mt.save()


class TestEditProtokollAttachmentAllowedView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/{}/edit/'
        self.view = views.edit_attachment
        self.use_attachment = True

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = accessible
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = accessible
        self.logged_in_protokollant = accessible
        self.admin_public = accessible
        self.admin_not_public = accessible

    def prepare_variables(self):
        super().prepare_variables()
        self.mt.attachment_protokoll = True
        self.mt.save()


class TestEditProtokollAttachmentNotAllowedView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/{}/edit/'
        self.view = views.edit_attachment
        self.use_attachment = True

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = not_found
        self.logged_in_protokollant = not_found
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.mt.attachment_protokoll = False
        self.mt.save()


class TestDelProtokollAttachmentAllowedView(TestEditProtokollAttachmentAllowedView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/{}/delete/'
        self.view = views.delete_attachment


class TestDelProtokollAttachmentNotAllowedView(TestEditProtokollAttachmentNotAllowedView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/{}/delete/'
        self.view = views.delete_attachment


class TestShowProtokollAttachmentAllowedView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/{}/'
        self.view = views.show_attachment
        self.use_attachment = True

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = accessible
        self.logged_in_with_admin_rights = permission_denied
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied
        self.logged_in_protokollant = permission_denied
        self.admin_public = accessible
        self.admin_not_public = accessible

    def prepare_variables(self):
        super().prepare_variables()
        self.mt.attachment_protokoll = True
        self.mt.save()
        self.protokoll.published = True
        self.protokoll.save()


class TestShowProtokollAttachmentNotAllowedView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/{}/'
        self.view = views.show_attachment
        self.use_attachment = True

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = not_found
        self.logged_in_with_admin_rights = permission_denied
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied
        self.logged_in_protokollant = permission_denied
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.mt.attachment_protokoll = False
        self.mt.save()


class TestShowProtokollWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/{}/'
        self.view = views.show_protokoll
        self.args = [self.filetype]
        self.redirect_url = '/protokolle/{}/{}/{}/'

        self.anonymous_public = not_found
        self.anonymous_not_public = not_found # TODO redirect_to_login
        self.logged_in_public = not_found
        self.logged_in_with_rights = not_found
        self.logged_in_with_admin_rights = not_found # TODO permission_denied
        self.logged_in_without_rights = not_found # TODO permission_denied
        self.logged_in_sitzungsleitung = not_found # TODO permission_denied
        self.logged_in_protokollant = not_found # TODO permission_denied
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.protokoll.approved = True
        self.protokoll.save()


class TestShowProtokollNotApprovedWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/{}/'
        self.view = views.show_protokoll
        self.args = [self.filetype]
        self.redirect_url = '/protokolle/{}/{}/{}/'

        self.anonymous_public = not_found
        self.anonymous_not_public = not_found # TODO redirect_to_login
        self.logged_in_public = not_found
        self.logged_in_with_rights = not_found
        self.logged_in_with_admin_rights = not_found # TODO permission_denied
        self.logged_in_without_rights = not_found # TODO permission_denied
        self.logged_in_sitzungsleitung = not_found # TODO permission_denied
        self.logged_in_protokollant = not_found # TODO permission_denied
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.protokoll.approved = False
        self.protokoll.save()


class TestShowPublicProtokollWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = '/protokolle/{}/{}/{}/'
        self.view = views.show_public_protokoll
        self.args = [self.filetype]
        self.redirect_url = '/{}/{}/protokoll/{}/'

        self.anonymous_public = not_found
        self.anonymous_not_public = not_found # TODO redirect_to_login
        self.logged_in_public = not_found # TODO redirect_to_url
        self.logged_in_with_rights = not_found
        self.logged_in_with_admin_rights = not_found # TODO permission_denied
        self.logged_in_without_rights = not_found # TODO permission_denied
        self.logged_in_sitzungsleitung = not_found # TODO permission_denied
        self.logged_in_protokollant = not_found # TODO permission_denied
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.protokoll.approved = True
        self.protokoll.save()


class TestShowPublicProtokollNotApprovedWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = '/protokolle/{}/{}/{}/'
        self.view = views.show_public_protokoll
        self.args = [self.filetype]
        self.redirect_url = '/{}/{}/protokoll/{}/'

        self.anonymous_public = not_found
        self.anonymous_not_public = not_found # TODO redirect_to_login
        self.logged_in_public = not_found
        self.logged_in_with_rights = not_found
        self.logged_in_with_admin_rights = not_found # TODO permission_denied
        self.logged_in_without_rights = not_found # TODO permission_denied
        self.logged_in_sitzungsleitung = not_found # TODO permission_denied
        self.logged_in_protokollant = not_found # TODO permission_denied
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.protokoll.approved = False
        self.protokoll.save()


class TestDownloadTemplatesOtherProtokollantWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/templates/'
        self.view = views.templates

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = accessible # TODO not_found
        self.logged_in_protokollant = accessible # TODO not_found
        self.admin_public = accessible # TODO not_found
        self.admin_not_public = accessible # TODO not_found

    def prepare_variables(self):
        super(TestDownloadTemplatesOtherProtokollantWrongMTView, self).prepare_variables()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestDownloadTemplatesNoProtokollantWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/templates/'
        self.view = views.templates

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied # TODO not_found
        self.logged_in_with_admin_rights = permission_denied # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = accessible # TODO not_found
        self.logged_in_protokollant = accessible # TODO not_found
        self.admin_public = accessible # TODO not_found
        self.admin_not_public = accessible # TODO not_found

    def prepare_variables(self):
        super(TestDownloadTemplatesNoProtokollantWrongMTView, self).prepare_variables()
        self.meeting.protokollant = None
        self.meeting.save()


class TestEditProtokollOtherProtokollantWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/edit/'
        self.view = views.edit_protokoll

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = accessible # TODO not_found
        self.logged_in_protokollant = accessible # TODO not_found
        self.admin_public = accessible # TODO not_found
        self.admin_not_public = accessible # TODO not_found

    def prepare_variables(self):
        super(TestEditProtokollOtherProtokollantWrongMTView, self).prepare_variables()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestPadOtherProtokollantWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/pad/'
        self.view = views.pad

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = ifthenelse(self.pad_test(), accessible, not_found) # TODO not_found
        self.logged_in_protokollant = ifthenelse(self.pad_test(), accessible, not_found) # TODO not_found
        self.admin_public = ifthenelse(self.pad_test(), accessible, not_found) # TODO not_found
        self.admin_not_public = ifthenelse(self.pad_test(), accessible, not_found) # TODO not_found

    def prepare_variables(self):
        super(TestPadOtherProtokollantWrongMTView, self).prepare_variables()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestEditProtokollNoProtokollantWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/edit/'
        self.view = views.edit_protokoll

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied # TODO not_found
        self.logged_in_with_admin_rights = permission_denied # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = accessible # TODO not_found
        self.logged_in_protokollant = accessible # TODO not_found
        self.admin_public = accessible # TODO not_found
        self.admin_not_public = accessible # TODO not_found

    def prepare_variables(self):
        super(TestEditProtokollNoProtokollantWrongMTView, self).prepare_variables()
        self.meeting.protokollant = None
        self.meeting.save()


class TestPadNoProtokollantWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/pad/'
        self.view = views.pad

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied # TODO not_found
        self.logged_in_with_admin_rights = permission_denied # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = ifthenelse(self.pad_test(), accessible, not_found) # TODO not_found
        self.logged_in_protokollant = ifthenelse(self.pad_test(), accessible, not_found) # TODO not_found
        self.admin_public = ifthenelse(self.pad_test(), accessible, not_found) # TODO not_found
        self.admin_not_public = ifthenelse(self.pad_test(), accessible, not_found) # TODO not_found

    def prepare_variables(self):
        super(TestPadNoProtokollantWrongMTView, self).prepare_variables()
        self.meeting.protokollant = None
        self.meeting.save()


class TestDelProtokollWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/delete/'
        self.view = views.delete_protokoll

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = accessible # TODO not_found
        self.logged_in_protokollant = permission_denied # TODO not_found
        self.admin_public = accessible # TODO not_found
        self.admin_not_public = accessible # TODO not_found


class TestProtokollSuccessWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/success/'
        self.view = views.success_protokoll

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = accessible # TODO not_found
        self.logged_in_protokollant = accessible # TODO not_found
        self.admin_public = accessible # TODO not_found
        self.admin_not_public = accessible # TODO not_found


class TestSendProtokollWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/send/'
        self.view = views.send_protokoll

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = error(AttributeError) # TODO not_found
        self.logged_in_protokollant = accessible # TODO not_found
        self.admin_public = error(AttributeError) # TODO not_found
        self.admin_not_public = error(AttributeError) # TODO not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.protokoll.published = True
        self.protokoll.save()


class TestProtokollAttachmentsAllowedWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/'
        self.view = views.attachments

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = accessible # TODO not_found
        self.logged_in_protokollant = accessible # TODO not_found
        self.admin_public = accessible # TODO not_found
        self.admin_not_public = accessible # TODO not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.mt2.attachment_protokoll = True
        self.mt2.save()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestProtokollAttachmentsNotAllowedWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/'
        self.view = views.attachments

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = not_found
        self.logged_in_protokollant = not_found
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.mt2.attachment_protokoll = False
        self.mt2.save()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestProtokollAttachmentsAllowedNoProtokollantWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/'
        self.view = views.attachments

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied # TODO not_found
        self.logged_in_with_admin_rights = permission_denied # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = accessible # TODO not_found
        self.logged_in_protokollant = accessible # TODO not_found
        self.admin_public = accessible # TODO not_found
        self.admin_not_public = accessible # TODO not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.mt2.attachment_protokoll = True
        self.mt2.save()
        self.meeting.protokollant = None
        self.meeting.save()


class TestProtokollAttachmentsNotAllowedNoProtokollantWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/'
        self.view = views.attachments

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied # TODO not_found
        self.logged_in_with_admin_rights = permission_denied # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = not_found
        self.logged_in_protokollant = not_found
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.mt2.attachment_protokoll = False
        self.mt2.save()
        self.meeting.protokollant = None
        self.meeting.save()


class TestSortProtokollAttachmentsAllowedWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/sort/'
        self.view = views.sort_attachments

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = bad_request # TODO not_found
        self.logged_in_protokollant = bad_request # TODO not_found
        self.admin_public = bad_request # TODO not_found
        self.admin_not_public = bad_request # TODO not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.mt2.attachment_protokoll = True
        self.mt2.save()


class TestSortProtokollAttachmentsNotAllowedWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/sort/'
        self.view = views.sort_attachments

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = not_found
        self.logged_in_protokollant = not_found
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.mt2.attachment_protokoll = False
        self.mt2.save()


class TestEditProtokollAttachmentAllowedWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/{}/edit/'
        self.view = views.edit_attachment
        self.use_attachment = True

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = accessible # TODO not_found
        self.logged_in_protokollant = accessible # TODO not_found
        self.admin_public = accessible # TODO not_found
        self.admin_not_public = accessible # TODO not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.mt2.attachment_protokoll = True
        self.mt2.save()


class TestEditProtokollAttachmentNotAllowedWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/{}/edit/'
        self.view = views.edit_attachment
        self.use_attachment = True

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = not_found
        self.logged_in_protokollant = not_found
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.mt2.attachment_protokoll = False
        self.mt2.save()


class TestDelProtokollAttachmentAllowedWrongMTView(TestEditProtokollAttachmentAllowedWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/{}/delete/'
        self.view = views.delete_attachment


class TestDelProtokollAttachmentNotAllowedWrongMTView(TestEditProtokollAttachmentNotAllowedWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/{}/delete/'
        self.view = views.delete_attachment


class TestShowProtokollAttachmentAllowedWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/{}/'
        self.view = views.show_attachment
        self.use_attachment = True

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied # TODO not_found
        self.logged_in_with_admin_rights = permission_denied
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied
        self.logged_in_protokollant = permission_denied
        self.admin_public = accessible # TODO not_found
        self.admin_not_public = accessible # TODO not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.mt2.attachment_protokoll = True
        self.mt2.save()


class TestShowProtokollAttachmentNotAllowedWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/{}/'
        self.view = views.show_attachment
        self.use_attachment = True

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied # TODO not_found
        self.logged_in_with_admin_rights = permission_denied
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied
        self.logged_in_protokollant = permission_denied
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.mt2.attachment_protokoll = False
        self.mt2.save()


class TestDownloadTemplatesOtherProtokollantImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/templates/'
        self.view = views.templates

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

    def prepare_variables(self):
        super(TestDownloadTemplatesOtherProtokollantImportedView, self).prepare_variables()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestDownloadTemplatesNoProtokollantImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/templates/'
        self.view = views.templates

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

    def prepare_variables(self):
        super(TestDownloadTemplatesNoProtokollantImportedView, self).prepare_variables()
        self.meeting.protokollant = None
        self.meeting.save()


class TestEditProtokollOtherProtokollantImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/edit/'
        self.view = views.edit_protokoll

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

    def prepare_variables(self):
        super(TestEditProtokollOtherProtokollantImportedView, self).prepare_variables()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestPadOtherProtokollantImportedView(TestEditProtokollOtherProtokollantImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/pad/'
        self.view = views.pad


class TestEditProtokollNoProtokollantImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/edit/'
        self.view = views.edit_protokoll

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

    def prepare_variables(self):
        super(TestEditProtokollNoProtokollantImportedView, self).prepare_variables()
        self.meeting.protokollant = None
        self.meeting.save()


class TestPadNoProtokollantImportedView(TestEditProtokollNoProtokollantImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/pad/'
        self.view = views.pad


class TestProtokollSuccessImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/success/'
        self.view = views.success_protokoll

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


class TestSendProtokollImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/send/'
        self.view = views.send_protokoll

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


class TestProtokollAttachmentsAllowedImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/'
        self.view = views.attachments

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

    def prepare_variables(self):
        super().prepare_variables()
        self.mt.attachment_protokoll = True
        self.mt.save()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestProtokollAttachmentsNotAllowedImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/'
        self.view = views.attachments

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

    def prepare_variables(self):
        super().prepare_variables()
        self.mt.attachment_protokoll = False
        self.mt.save()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestProtokollAttachmentsAllowedNoProtokollantImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/'
        self.view = views.attachments

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

    def prepare_variables(self):
        super().prepare_variables()
        self.mt.attachment_protokoll = True
        self.mt.save()
        self.meeting.protokollant = None
        self.meeting.save()


class TestProtokollAttachmentsNotAllowedNoProtokollantImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/'
        self.view = views.attachments

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

    def prepare_variables(self):
        super().prepare_variables()
        self.mt.attachment_protokoll = False
        self.mt.save()
        self.meeting.protokollant = None
        self.meeting.save()


class TestSortProtokollAttachmentsAllowedImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/sort/'
        self.view = views.sort_attachments

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

    def prepare_variables(self):
        super().prepare_variables()
        self.mt.attachment_protokoll = True
        self.mt.save()


class TestSortProtokollAttachmentsNotAllowedImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/sort/'
        self.view = views.sort_attachments

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

    def prepare_variables(self):
        super().prepare_variables()
        self.mt.attachment_protokoll = False
        self.mt.save()


class TestEditProtokollAttachmentAllowedImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/{}/edit/'
        self.view = views.edit_attachment
        self.use_attachment = True

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

    def prepare_variables(self):
        super().prepare_variables()
        self.mt.attachment_protokoll = True
        self.mt.save()


class TestEditProtokollAttachmentNotAllowedImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/{}/edit/'
        self.view = views.edit_attachment
        self.use_attachment = True

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

    def prepare_variables(self):
        super().prepare_variables()
        self.mt.attachment_protokoll = False
        self.mt.save()


class TestDelProtokollAttachmentAllowedImportedView(TestEditProtokollAttachmentAllowedImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/{}/delete/'
        self.view = views.delete_attachment


class TestDelProtokollAttachmentNotAllowedImportedView(TestEditProtokollAttachmentNotAllowedImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/{}/delete/'
        self.view = views.delete_attachment


class TestShowProtokollAttachmentAllowedImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/{}/'
        self.view = views.show_attachment
        self.use_attachment = True

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

    def prepare_variables(self):
        super().prepare_variables()
        self.mt.attachment_protokoll = True
        self.mt.save()


class TestShowProtokollAttachmentNotAllowedImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = '/{}/{}/protokoll/attachments/{}/'
        self.view = views.show_attachment
        self.use_attachment = True

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

    def prepare_variables(self):
        super().prepare_variables()
        self.mt.attachment_protokoll = False
        self.mt.save()
