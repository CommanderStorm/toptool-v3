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


class TestShowEmptyTemplateView(AbstractTestView):
    def setup_method(self):
        super(TestShowEmptyTemplateView, self).setup_method()
        self.win = random.choice((True, False))
        self.url = '/{}/{}/template/'
        if self.win:
            self.url += "{}/"
            self.args.append("win")
        self.view = views.template

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = redirect_to_login
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = accessible
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = accessible
        self.logged_in_protokollant = permission_denied # TODO accessible
        self.admin_public = accessible
        self.admin_not_public = accessible


#   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/template/(?:(?P<newline_style>win)/)?$',
#       views.template, name="template"),
#   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/templatefilled/(?:(?P<newline_style>win)/)?$',
#       views.template_filled, name="templatefilled"),
#   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/editprotokoll/$', views.edit_protokoll,
#       name="editprotokoll"),
#   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/delprotokoll$', views.delete_protokoll,
#       name="delprotokoll"),
#   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/protokollsuccess$',
#       views.success_protokoll, name="successprotokoll"),
#   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/sendprotokoll$', views.send_protokoll,
#       name="sendprotokoll"),
#   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/attachments/$', views.attachments,
#       name="attachments"),
#   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/attachments/sort/$',
#       views.sort_attachments, name="sortattachments"),
#   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/attachments/(?P<attachment_pk>[0-9]+)/$',
#       views.show_attachment, name="showattachment_protokoll"),
#   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/attachments/(?P<attachment_pk>[0-9]+)/edit/$',
#       views.edit_attachment, name="editattachment"),
#   url(r'^(?P<meeting_pk>[0-9a-f\-]+)/attachments/(?P<attachment_pk>[0-9]+)/delete/$',
