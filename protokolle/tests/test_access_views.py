import datetime
import random

from django.utils import timezone

from toptool.tests.access import *
from toptool_common.views import next_view
from .. import views


class TestShowProtokollView(AbstractTestView):
    def setup_method(self):
        super(TestShowProtokollView, self).setup_method()
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
        super(TestShowProtokollView, self).prepare_variables()
        self.protokoll.approved = True
        self.protokoll.save()


class TestShowProtokollNotApprovedView(AbstractTestView):
    def setup_method(self):
        super(TestShowProtokollNotApprovedView, self).setup_method()
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
        super(TestShowProtokollNotApprovedView, self).prepare_variables()
        self.protokoll.approved = False
        self.protokoll.save()


class TestShowPublicProtokollView(AbstractTestView):
    def setup_method(self):
        super(TestShowPublicProtokollView, self).setup_method()
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
        super(TestShowPublicProtokollView, self).prepare_variables()
        self.protokoll.approved = True
        self.protokoll.save()


class TestShowPublicProtokollNotApprovedView(AbstractTestView):
    def setup_method(self):
        super(TestShowPublicProtokollNotApprovedView, self).setup_method()
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
        super(TestShowPublicProtokollNotApprovedView, self).prepare_variables()
        self.protokoll.approved = False
        self.protokoll.save()


class TestShowEmptyTemplateOtherProtokollantView(AbstractTestView):
    def setup_method(self):
        super(TestShowEmptyTemplateOtherProtokollantView, self).setup_method()
        self.win = random.choice((True, False))
        self.url = '/{}/{}/template/'
        if self.win:
            self.url += "{}/"
            self.args.append("win")
        self.view = views.template

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = accessible # TODO permission_denied
        self.logged_in_with_admin_rights = permission_denied # TODO accessible
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied # TODO accessible
        self.logged_in_protokollant = permission_denied # TODO accessible
        self.admin_public = accessible
        self.admin_not_public = accessible

    def prepare_variables(self):
        super(TestShowEmptyTemplateOtherProtokollantView, self).prepare_variables()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestShowEmptyTemplateNoProtokollantView(AbstractTestView):
    def setup_method(self):
        super(TestShowEmptyTemplateNoProtokollantView, self).setup_method()
        self.win = random.choice((True, False))
        self.url = '/{}/{}/template/'
        if self.win:
            self.url += "{}/"
            self.args.append("win")
        self.view = views.template

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = accessible
        self.logged_in_with_admin_rights = permission_denied # TODO accessible
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied # TODO accessible
        self.logged_in_protokollant = permission_denied # TODO accessible
        self.admin_public = accessible
        self.admin_not_public = accessible

    def prepare_variables(self):
        super(TestShowEmptyTemplateNoProtokollantView, self).prepare_variables()
        self.meeting.protokollant = None
        self.meeting.save()


class TestShowFilledTemplateView(AbstractTestView):
    def setup_method(self):
        super(TestShowFilledTemplateView, self).setup_method()
        self.win = random.choice((True, False))
        self.url = '/{}/{}/templatefilled/'
        if self.win:
            self.url += "{}/"
            self.args.append("win")
        self.view = views.template_filled

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


class TestEditProtokollOtherProtokollantView(AbstractTestView):
    def setup_method(self):
        super(TestEditProtokollOtherProtokollantView, self).setup_method()
        self.url = '/{}/{}/editprotokoll/'
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


class TestEditProtokollNoProtokollantView(AbstractTestView):
    def setup_method(self):
        super(TestEditProtokollNoProtokollantView, self).setup_method()
        self.url = '/{}/{}/editprotokoll/'
        self.view = views.edit_protokoll

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = accessible
        self.logged_in_with_admin_rights = permission_denied # TODO accessible
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied # TODO accessible
        self.logged_in_protokollant = accessible
        self.admin_public = accessible
        self.admin_not_public = accessible

    def prepare_variables(self):
        super(TestEditProtokollNoProtokollantView, self).prepare_variables()
        self.meeting.protokollant = None
        self.meeting.save()


class TestDelProtokollView(AbstractTestView):
    def setup_method(self):
        super(TestDelProtokollView, self).setup_method()
        self.url = '/{}/{}/delprotokoll/'
        self.view = views.delete_protokoll

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


class TestProtokollSuccessView(AbstractTestView):
    def setup_method(self):
        super(TestProtokollSuccessView, self).setup_method()
        self.url = '/{}/{}/protokollsuccess/'
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
        super(TestSendProtokollView, self).setup_method()
        self.url = '/{}/{}/sendprotokoll/'
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


class TestProtokollAttachmentsAllowedView(AbstractTestView):
    def setup_method(self):
        super(TestProtokollAttachmentsAllowedView, self).setup_method()
        self.url = '/{}/{}/attachments/'
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
        super(TestProtokollAttachmentsAllowedView, self).prepare_variables()
        self.mt.attachment_protokoll = True
        self.mt.save()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestProtokollAttachmentsNotAllowedView(AbstractTestView):
    def setup_method(self):
        super(TestProtokollAttachmentsNotAllowedView, self).setup_method()
        self.url = '/{}/{}/attachments/'
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
        super(TestProtokollAttachmentsNotAllowedView, self).prepare_variables()
        self.mt.attachment_protokoll = False
        self.mt.save()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestProtokollAttachmentsAllowedNoProtokollantView(AbstractTestView):
    def setup_method(self):
        super(TestProtokollAttachmentsAllowedNoProtokollantView, self).setup_method()
        self.url = '/{}/{}/attachments/'
        self.view = views.attachments

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = accessible
        self.logged_in_with_admin_rights = permission_denied # TODO accessible
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied # TODO accessible
        self.logged_in_protokollant = accessible
        self.admin_public = accessible
        self.admin_not_public = accessible

    def prepare_variables(self):
        super(TestProtokollAttachmentsAllowedNoProtokollantView, self).prepare_variables()
        self.mt.attachment_protokoll = True
        self.mt.save()
        self.meeting.protokollant = None
        self.meeting.save()


class TestProtokollAttachmentsNotAllowedNoProtokollantView(AbstractTestView):
    def setup_method(self):
        super(TestProtokollAttachmentsNotAllowedNoProtokollantView, self).setup_method()
        self.url = '/{}/{}/attachments/'
        self.view = views.attachments

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = not_found
        self.logged_in_with_admin_rights = permission_denied # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied # TODO not_found
        self.logged_in_protokollant = not_found
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super(TestProtokollAttachmentsNotAllowedNoProtokollantView, self).prepare_variables()
        self.mt.attachment_protokoll = False
        self.mt.save()
        self.meeting.protokollant = None
        self.meeting.save()


class TestSortProtokollAttachmentsAllowedView(AbstractTestView):
    def setup_method(self):
        super(TestSortProtokollAttachmentsAllowedView, self).setup_method()
        self.url = '/{}/{}/attachments/sort/'
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
        super(TestSortProtokollAttachmentsAllowedView, self).prepare_variables()
        self.mt.attachment_protokoll = True
        self.mt.save()


class TestSortProtokollAttachmentsNotAllowedView(AbstractTestView):
    def setup_method(self):
        super(TestSortProtokollAttachmentsNotAllowedView, self).setup_method()
        self.url = '/{}/{}/attachments/sort/'
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
        super(TestSortProtokollAttachmentsNotAllowedView, self).prepare_variables()
        self.mt.attachment_protokoll = False
        self.mt.save()


class TestEditProtokollAttachmentAllowedView(AbstractTestView):
    def setup_method(self):
        super(TestEditProtokollAttachmentAllowedView, self).setup_method()
        self.url = '/{}/{}/attachments/{}/edit/'
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
        super(TestEditProtokollAttachmentAllowedView, self).prepare_variables()
        self.mt.attachment_protokoll = True
        self.mt.save()


class TestEditProtokollAttachmentNotAllowedView(AbstractTestView):
    def setup_method(self):
        super(TestEditProtokollAttachmentNotAllowedView, self).setup_method()
        self.url = '/{}/{}/attachments/{}/edit/'
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
        super(TestEditProtokollAttachmentNotAllowedView, self).prepare_variables()
        self.mt.attachment_protokoll = False
        self.mt.save()


class TestDelProtokollAttachmentAllowedView(TestEditProtokollAttachmentAllowedView):
    def setup_method(self):
        super(TestDelProtokollAttachmentAllowedView, self).setup_method()
        self.url = '/{}/{}/attachments/{}/del/'
        self.view = views.delete_attachment


class TestDelProtokollAttachmentNotAllowedView(TestEditProtokollAttachmentNotAllowedView):
    def setup_method(self):
        super(TestDelProtokollAttachmentNotAllowedView, self).setup_method()
        self.url = '/{}/{}/attachments/{}/del/'
        self.view = views.delete_attachment


class TestShowProtokollAttachmentAllowedView(AbstractTestView):
    def setup_method(self):
        super(TestShowProtokollAttachmentAllowedView, self).setup_method()
        self.url = '/{}/{}/attachments/{}/'
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
        super(TestShowProtokollAttachmentAllowedView, self).prepare_variables()
        self.mt.attachment_protokoll = True
        self.mt.save()


class TestShowProtokollAttachmentNotAllowedView(AbstractTestView):
    def setup_method(self):
        super(TestShowProtokollAttachmentNotAllowedView, self).setup_method()
        self.url = '/{}/{}/attachments/{}/'
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
        super(TestShowProtokollAttachmentNotAllowedView, self).prepare_variables()
        self.mt.attachment_protokoll = False
        self.mt.save()


class TestShowProtokollWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super(TestShowProtokollWrongMTView, self).setup_method()
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
        super(TestShowProtokollWrongMTView, self).prepare_variables()
        self.protokoll.approved = True
        self.protokoll.save()


class TestShowProtokollNotApprovedWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super(TestShowProtokollNotApprovedWrongMTView, self).setup_method()
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
        super(TestShowProtokollNotApprovedWrongMTView, self).prepare_variables()
        self.protokoll.approved = False
        self.protokoll.save()


class TestShowPublicProtokollWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super(TestShowPublicProtokollWrongMTView, self).setup_method()
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
        super(TestShowPublicProtokollWrongMTView, self).prepare_variables()
        self.protokoll.approved = True
        self.protokoll.save()


class TestShowPublicProtokollNotApprovedWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super(TestShowPublicProtokollNotApprovedWrongMTView, self).setup_method()
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
        super(TestShowPublicProtokollNotApprovedWrongMTView, self).prepare_variables()
        self.protokoll.approved = False
        self.protokoll.save()


class TestShowEmptyTemplateOtherProtokollantWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super(TestShowEmptyTemplateOtherProtokollantWrongMTView, self).setup_method()
        self.win = random.choice((True, False))
        self.url = '/{}/{}/template/'
        if self.win:
            self.url += "{}/"
            self.args.append("win")
        self.view = views.template

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied # TODO not_found
        self.logged_in_protokollant = permission_denied # TODO not_found
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super(TestShowEmptyTemplateOtherProtokollantWrongMTView, self).prepare_variables()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestShowEmptyTemplateNoProtokollantWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super(TestShowEmptyTemplateNoProtokollantWrongMTView, self).setup_method()
        self.win = random.choice((True, False))
        self.url = '/{}/{}/template/'
        if self.win:
            self.url += "{}/"
            self.args.append("win")
        self.view = views.template

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied # TODO not_found
        self.logged_in_with_admin_rights = permission_denied # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied # TODO not_found
        self.logged_in_protokollant = permission_denied # TODO not_found
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super(TestShowEmptyTemplateNoProtokollantWrongMTView, self).prepare_variables()
        self.meeting.protokollant = None
        self.meeting.save()


class TestShowFilledTemplateWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super(TestShowFilledTemplateWrongMTView, self).setup_method()
        self.win = random.choice((True, False))
        self.url = '/{}/{}/templatefilled/'
        if self.win:
            self.url += "{}/"
            self.args.append("win")
        self.view = views.template_filled

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


class TestEditProtokollOtherProtokollantWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super(TestEditProtokollOtherProtokollantWrongMTView, self).setup_method()
        self.url = '/{}/{}/editprotokoll/'
        self.view = views.edit_protokoll

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
        super(TestEditProtokollOtherProtokollantWrongMTView, self).prepare_variables()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestEditProtokollNoProtokollantWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super(TestEditProtokollNoProtokollantWrongMTView, self).setup_method()
        self.url = '/{}/{}/editprotokoll/'
        self.view = views.edit_protokoll

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied # TODO not_found
        self.logged_in_with_admin_rights = permission_denied # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied # TODO not_found
        self.logged_in_protokollant = not_found
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super(TestEditProtokollNoProtokollantWrongMTView, self).prepare_variables()
        self.meeting.protokollant = None
        self.meeting.save()


class TestDelProtokollWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super(TestDelProtokollWrongMTView, self).setup_method()
        self.url = '/{}/{}/delprotokoll/'
        self.view = views.delete_protokoll

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


class TestProtokollSuccessWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super(TestProtokollSuccessWrongMTView, self).setup_method()
        self.url = '/{}/{}/protokollsuccess/'
        self.view = views.success_protokoll

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


class TestSendProtokollWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super(TestSendProtokollWrongMTView, self).setup_method()
        self.url = '/{}/{}/sendprotokoll/'
        self.view = views.send_protokoll

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = error(AttributeError) # TODO not_found
        self.logged_in_protokollant = not_found
        self.admin_public = error(AttributeError) # TODO not_found
        self.admin_not_public = error(AttributeError) # TODO not_found


class TestProtokollAttachmentsAllowedWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super(TestProtokollAttachmentsAllowedWrongMTView, self).setup_method()
        self.url = '/{}/{}/attachments/'
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
        super(TestProtokollAttachmentsAllowedWrongMTView, self).prepare_variables()
        self.mt.attachment_protokoll = True
        self.mt.save()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestProtokollAttachmentsNotAllowedWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super(TestProtokollAttachmentsNotAllowedWrongMTView, self).setup_method()
        self.url = '/{}/{}/attachments/'
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
        super(TestProtokollAttachmentsNotAllowedWrongMTView, self).prepare_variables()
        self.mt.attachment_protokoll = False
        self.mt.save()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestProtokollAttachmentsAllowedNoProtokollantWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super(TestProtokollAttachmentsAllowedNoProtokollantWrongMTView, self).setup_method()
        self.url = '/{}/{}/attachments/'
        self.view = views.attachments

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied # TODO not_found
        self.logged_in_with_admin_rights = permission_denied # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied # TODO not_found
        self.logged_in_protokollant = not_found
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super(TestProtokollAttachmentsAllowedNoProtokollantWrongMTView, self).prepare_variables()
        self.mt.attachment_protokoll = True
        self.mt.save()
        self.meeting.protokollant = None
        self.meeting.save()


class TestProtokollAttachmentsNotAllowedNoProtokollantWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super(TestProtokollAttachmentsNotAllowedNoProtokollantWrongMTView, self).setup_method()
        self.url = '/{}/{}/attachments/'
        self.view = views.attachments

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied # TODO not_found
        self.logged_in_with_admin_rights = permission_denied # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied # TODO not_found
        self.logged_in_protokollant = not_found
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super(TestProtokollAttachmentsNotAllowedNoProtokollantWrongMTView, self).prepare_variables()
        self.mt.attachment_protokoll = False
        self.mt.save()
        self.meeting.protokollant = None
        self.meeting.save()


class TestSortProtokollAttachmentsAllowedWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super(TestSortProtokollAttachmentsAllowedWrongMTView, self).setup_method()
        self.url = '/{}/{}/attachments/sort/'
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
        super(TestSortProtokollAttachmentsAllowedWrongMTView, self).prepare_variables()
        self.mt.attachment_protokoll = True
        self.mt.save()


class TestSortProtokollAttachmentsNotAllowedWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super(TestSortProtokollAttachmentsNotAllowedWrongMTView, self).setup_method()
        self.url = '/{}/{}/attachments/sort/'
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
        super(TestSortProtokollAttachmentsNotAllowedWrongMTView, self).prepare_variables()
        self.mt.attachment_protokoll = False
        self.mt.save()


class TestEditProtokollAttachmentAllowedWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super(TestEditProtokollAttachmentAllowedWrongMTView, self).setup_method()
        self.url = '/{}/{}/attachments/{}/edit/'
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
        super(TestEditProtokollAttachmentAllowedWrongMTView, self).prepare_variables()
        self.mt.attachment_protokoll = True
        self.mt.save()


class TestEditProtokollAttachmentNotAllowedWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super(TestEditProtokollAttachmentNotAllowedWrongMTView, self).setup_method()
        self.url = '/{}/{}/attachments/{}/edit/'
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
        super(TestEditProtokollAttachmentNotAllowedWrongMTView, self).prepare_variables()
        self.mt.attachment_protokoll = False
        self.mt.save()


class TestDelProtokollAttachmentAllowedWrongMTView(TestEditProtokollAttachmentAllowedWrongMTView):
    def setup_method(self):
        super(TestDelProtokollAttachmentAllowedWrongMTView, self).setup_method()
        self.url = '/{}/{}/attachments/{}/del/'
        self.view = views.delete_attachment


class TestDelProtokollAttachmentNotAllowedWrongMTView(TestEditProtokollAttachmentNotAllowedWrongMTView):
    def setup_method(self):
        super(TestDelProtokollAttachmentNotAllowedWrongMTView, self).setup_method()
        self.url = '/{}/{}/attachments/{}/del/'
        self.view = views.delete_attachment


class TestShowProtokollAttachmentAllowedWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super(TestShowProtokollAttachmentAllowedWrongMTView, self).setup_method()
        self.url = '/{}/{}/attachments/{}/'
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
        super(TestShowProtokollAttachmentAllowedWrongMTView, self).prepare_variables()
        self.mt.attachment_protokoll = True
        self.mt.save()


class TestShowProtokollAttachmentNotAllowedWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super(TestShowProtokollAttachmentNotAllowedWrongMTView, self).setup_method()
        self.url = '/{}/{}/attachments/{}/'
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
        super(TestShowProtokollAttachmentNotAllowedWrongMTView, self).prepare_variables()
        self.mt.attachment_protokoll = False
        self.mt.save()


class TestShowEmptyTemplateOtherProtokollantImportedView(AbstractTestImportedView):
    def setup_method(self):
        super(TestShowEmptyTemplateOtherProtokollantImportedView, self).setup_method()
        self.win = random.choice((True, False))
        self.url = '/{}/{}/template/'
        if self.win:
            self.url += "{}/"
            self.args.append("win")
        self.view = views.template

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
        super(TestShowEmptyTemplateOtherProtokollantImportedView, self).prepare_variables()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestShowEmptyTemplateNoProtokollantImportedView(AbstractTestImportedView):
    def setup_method(self):
        super(TestShowEmptyTemplateNoProtokollantImportedView, self).setup_method()
        self.win = random.choice((True, False))
        self.url = '/{}/{}/template/'
        if self.win:
            self.url += "{}/"
            self.args.append("win")
        self.view = views.template

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
        super(TestShowEmptyTemplateNoProtokollantImportedView, self).prepare_variables()
        self.meeting.protokollant = None
        self.meeting.save()


class TestShowFilledTemplateImportedView(AbstractTestImportedView):
    def setup_method(self):
        super(TestShowFilledTemplateImportedView, self).setup_method()
        self.win = random.choice((True, False))
        self.url = '/{}/{}/templatefilled/'
        if self.win:
            self.url += "{}/"
            self.args.append("win")
        self.view = views.template_filled

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


class TestEditProtokollOtherProtokollantImportedView(AbstractTestImportedView):
    def setup_method(self):
        super(TestEditProtokollOtherProtokollantImportedView, self).setup_method()
        self.url = '/{}/{}/editprotokoll/'
        self.view = views.edit_protokoll

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = accessible # TODO permission_denied
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = accessible # TODO permission_denied
        self.logged_in_protokollant = accessible # TODO permission_denied
        self.admin_public = accessible # TODO permission_denied
        self.admin_not_public = accessible # TODO permission_denied

    def prepare_variables(self):
        super(TestEditProtokollOtherProtokollantImportedView, self).prepare_variables()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestEditProtokollNoProtokollantImportedView(AbstractTestImportedView):
    def setup_method(self):
        super(TestEditProtokollNoProtokollantImportedView, self).setup_method()
        self.url = '/{}/{}/editprotokoll/'
        self.view = views.edit_protokoll

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied
        self.logged_in_protokollant = accessible # TODO permission_denied
        self.admin_public = permission_denied
        self.admin_not_public = permission_denied

    def prepare_variables(self):
        super(TestEditProtokollNoProtokollantImportedView, self).prepare_variables()
        self.meeting.protokollant = None
        self.meeting.save()


class TestProtokollSuccessImportedView(AbstractTestImportedView):
    def setup_method(self):
        super(TestProtokollSuccessImportedView, self).setup_method()
        self.url = '/{}/{}/protokollsuccess/'
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
        super(TestSendProtokollImportedView, self).setup_method()
        self.url = '/{}/{}/sendprotokoll/'
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
        super(TestProtokollAttachmentsAllowedImportedView, self).setup_method()
        self.url = '/{}/{}/attachments/'
        self.view = views.attachments

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = accessible # TODO permission_denied
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = accessible # TODO permission_denied
        self.logged_in_protokollant = accessible # TODO permission_denied
        self.admin_public = accessible # TODO permission_denied
        self.admin_not_public = accessible # TODO permission_denied

    def prepare_variables(self):
        super(TestProtokollAttachmentsAllowedImportedView, self).prepare_variables()
        self.mt.attachment_protokoll = True
        self.mt.save()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestProtokollAttachmentsNotAllowedImportedView(AbstractTestImportedView):
    def setup_method(self):
        super(TestProtokollAttachmentsNotAllowedImportedView, self).setup_method()
        self.url = '/{}/{}/attachments/'
        self.view = views.attachments

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = not_found # TODO permission_denied
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = not_found # TODO permission_denied
        self.logged_in_protokollant = not_found # TODO permission_denied
        self.admin_public = not_found # TODO permission_denied
        self.admin_not_public = not_found # TODO permission_denied

    def prepare_variables(self):
        super(TestProtokollAttachmentsNotAllowedImportedView, self).prepare_variables()
        self.mt.attachment_protokoll = False
        self.mt.save()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestProtokollAttachmentsAllowedNoProtokollantImportedView(AbstractTestImportedView):
    def setup_method(self):
        super(TestProtokollAttachmentsAllowedNoProtokollantImportedView, self).setup_method()
        self.url = '/{}/{}/attachments/'
        self.view = views.attachments

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied
        self.logged_in_protokollant = accessible # TODO permission_denied
        self.admin_public = permission_denied
        self.admin_not_public = permission_denied

    def prepare_variables(self):
        super(TestProtokollAttachmentsAllowedNoProtokollantImportedView, self).prepare_variables()
        self.mt.attachment_protokoll = True
        self.mt.save()
        self.meeting.protokollant = None
        self.meeting.save()


class TestProtokollAttachmentsNotAllowedNoProtokollantImportedView(AbstractTestImportedView):
    def setup_method(self):
        super(TestProtokollAttachmentsNotAllowedNoProtokollantImportedView, self).setup_method()
        self.url = '/{}/{}/attachments/'
        self.view = views.attachments

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied
        self.logged_in_protokollant = not_found # TODO permission_denied
        self.admin_public = permission_denied
        self.admin_not_public = permission_denied

    def prepare_variables(self):
        super(TestProtokollAttachmentsNotAllowedNoProtokollantImportedView, self).prepare_variables()
        self.mt.attachment_protokoll = False
        self.mt.save()
        self.meeting.protokollant = None
        self.meeting.save()


class TestSortProtokollAttachmentsAllowedImportedView(AbstractTestImportedView):
    def setup_method(self):
        super(TestSortProtokollAttachmentsAllowedImportedView, self).setup_method()
        self.url = '/{}/{}/attachments/sort/'
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
        super(TestSortProtokollAttachmentsAllowedImportedView, self).prepare_variables()
        self.mt.attachment_protokoll = True
        self.mt.save()


class TestSortProtokollAttachmentsNotAllowedImportedView(AbstractTestImportedView):
    def setup_method(self):
        super(TestSortProtokollAttachmentsNotAllowedImportedView, self).setup_method()
        self.url = '/{}/{}/attachments/sort/'
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
        super(TestSortProtokollAttachmentsNotAllowedImportedView, self).prepare_variables()
        self.mt.attachment_protokoll = False
        self.mt.save()


class TestEditProtokollAttachmentAllowedImportedView(AbstractTestImportedView):
    def setup_method(self):
        super(TestEditProtokollAttachmentAllowedImportedView, self).setup_method()
        self.url = '/{}/{}/attachments/{}/edit/'
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
        super(TestEditProtokollAttachmentAllowedImportedView, self).prepare_variables()
        self.mt.attachment_protokoll = True
        self.mt.save()


class TestEditProtokollAttachmentNotAllowedImportedView(AbstractTestImportedView):
    def setup_method(self):
        super(TestEditProtokollAttachmentNotAllowedImportedView, self).setup_method()
        self.url = '/{}/{}/attachments/{}/edit/'
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
        super(TestEditProtokollAttachmentNotAllowedImportedView, self).prepare_variables()
        self.mt.attachment_protokoll = False
        self.mt.save()


class TestDelProtokollAttachmentAllowedImportedView(TestEditProtokollAttachmentAllowedImportedView):
    def setup_method(self):
        super(TestDelProtokollAttachmentAllowedImportedView, self).setup_method()
        self.url = '/{}/{}/attachments/{}/del/'
        self.view = views.delete_attachment


class TestDelProtokollAttachmentNotAllowedImportedView(TestEditProtokollAttachmentNotAllowedImportedView):
    def setup_method(self):
        super(TestDelProtokollAttachmentNotAllowedImportedView, self).setup_method()
        self.url = '/{}/{}/attachments/{}/del/'
        self.view = views.delete_attachment


class TestShowProtokollAttachmentAllowedImportedView(AbstractTestImportedView):
    def setup_method(self):
        super(TestShowProtokollAttachmentAllowedImportedView, self).setup_method()
        self.url = '/{}/{}/attachments/{}/'
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
        super(TestShowProtokollAttachmentAllowedImportedView, self).prepare_variables()
        self.mt.attachment_protokoll = True
        self.mt.save()


class TestShowProtokollAttachmentNotAllowedImportedView(AbstractTestImportedView):
    def setup_method(self):
        super(TestShowProtokollAttachmentNotAllowedImportedView, self).setup_method()
        self.url = '/{}/{}/attachments/{}/'
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
        super(TestShowProtokollAttachmentNotAllowedImportedView, self).prepare_variables()
        self.mt.attachment_protokoll = False
        self.mt.save()
