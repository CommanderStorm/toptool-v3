import datetime
import random

from django.utils import timezone

from toptool.tests.access import *
from .. import views


class TestAddAttendeesView(AbstractTestView):
    def setup_method(self):
        super(TestAddAttendeesView, self).setup_method()
        self.url = '/{}/{}/addatt/'
        self.view = views.add_attendees

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
        super(TestAddAttendeesView, self).prepare_variables()
        self.mt.attendance = True
        self.mt.save()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestAddAttendeesNoProtokollantView(AbstractTestView):
    def setup_method(self):
        super(TestAddAttendeesNoProtokollantView, self).setup_method()
        self.url = '/{}/{}/addatt/'
        self.view = views.add_attendees

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
        super(TestAddAttendeesNoProtokollantView, self).prepare_variables()
        self.mt.attendance = True
        self.mt.save()
        self.meeting.protokollant = None
        self.meeting.save()


class TestAddAttendeesNotAllowedView(AbstractTestView):
    def setup_method(self):
        super(TestAddAttendeesNotAllowedView, self).setup_method()
        self.url = '/{}/{}/addatt/'
        self.view = views.add_attendees

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
        super(TestAddAttendeesNotAllowedView, self).prepare_variables()
        self.mt.attendance = False
        self.mt.save()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestAddAttendeesNANPView(AbstractTestView):
    def setup_method(self):
        super(TestAddAttendeesNANPView, self).setup_method()
        self.url = '/{}/{}/addatt/'
        self.view = views.add_attendees

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
        super(TestAddAttendeesNANPView, self).prepare_variables()
        self.mt.attendance = False
        self.mt.save()
        self.meeting.protokollant = None
        self.meeting.save()


class TestEditAttendeeYYView(AbstractTestView):
    def setup_method(self):
        super(TestEditAttendeeYYView, self).setup_method()
        self.url = '/{}/{}/editatt/{}/'
        self.view = views.edit_attendee
        self.use_attendee = True

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
        super(TestEditAttendeeYYView, self).prepare_variables()
        self.mt.attendance = True
        self.mt.attendance_with_func = True
        self.mt.save()


class TestEditAttendeeNoAttendanceView(AbstractTestView):
    def setup_method(self):
        super(TestEditAttendeeNoAttendanceView, self).setup_method()
        self.url = '/{}/{}/editatt/{}/'
        self.view = views.edit_attendee
        self.use_attendee = True

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
        super(TestEditAttendeeNoAttendanceView, self).prepare_variables()
        self.mt.attendance = False
        self.mt.save()


class TestEditAttendeeNoAttendanceFuncView(AbstractTestView):
    def setup_method(self):
        super(TestEditAttendeeNoAttendanceFuncView, self).setup_method()
        self.url = '/{}/{}/editatt/{}/'
        self.view = views.edit_attendee
        self.use_attendee = True

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
        super(TestEditAttendeeNoAttendanceFuncView, self).prepare_variables()
        self.mt.attendance_with_func = False
        self.mt.save()


class TestDeleteAttendeeView(AbstractTestView):
    def setup_method(self):
        super(TestDeleteAttendeeView, self).setup_method()
        self.url = '/{}/{}/delatt/{}/'
        self.view = views.delete_attendee
        self.use_attendee = True
        self.redirect_url = '/{}/{}/addatt/'

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = redirect_to_url
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = redirect_to_url
        self.logged_in_protokollant = redirect_to_url
        self.admin_public = redirect_to_url
        self.admin_not_public = redirect_to_url

    def prepare_variables(self):
        super(TestDeleteAttendeeView, self).prepare_variables()
        self.mt.attendance = True
        self.mt.save()


class TestDeleteAttendeeNoAttendanceView(AbstractTestView):
    def setup_method(self):
        super(TestDeleteAttendeeNoAttendanceView, self).setup_method()
        self.url = '/{}/{}/delatt/{}/'
        self.view = views.delete_attendee
        self.use_attendee = True

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
        super(TestDeleteAttendeeNoAttendanceView, self).prepare_variables()
        self.mt.attendance = False
        self.mt.save()


class TestShowFunctionsView(AbstractTestView):
    def setup_method(self):
        super(TestShowFunctionsView, self).setup_method()
        self.url = '/{}/functions/'
        self.view = views.functions
        self.use_meeting = False

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

    def prepare_variables(self):
        super(TestShowFunctionsView, self).prepare_variables()
        self.mt.attendance = True
        self.mt.attendance_with_func = True
        self.mt.save()


class TestShowFunctionsNoAttandanceView(AbstractTestView):
    def setup_method(self):
        super(TestShowFunctionsNoAttandanceView, self).setup_method()
        self.url = '/{}/functions/'
        self.view = views.functions
        self.use_meeting = False

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied
        self.logged_in_protokollant = permission_denied
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super(TestShowFunctionsNoAttandanceView, self).prepare_variables()
        self.mt.attendance = False
        self.mt.save()

class TestShowFunctionsNoAttandanceFuncView(TestShowFunctionsNoAttandanceView):
    def prepare_variables(self):
        super(TestShowFunctionsNoAttandanceView, self).prepare_variables()
        self.mt.attendance_with_func = False
        self.mt.save()


class TestSortFunctionsView(AbstractTestView):
    def setup_method(self):
        super(TestSortFunctionsView, self).setup_method()
        self.url = '/{}/functions/sort/'
        self.view = views.sort_functions
        self.use_meeting = False

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = bad_request
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied
        self.logged_in_protokollant = permission_denied
        self.admin_public = bad_request
        self.admin_not_public = bad_request

    def prepare_variables(self):
        super(TestSortFunctionsView, self).prepare_variables()
        self.mt.attendance = True
        self.mt.attendance_with_func = True
        self.mt.save()


class TestSortFunctionsNoAttandanceView(AbstractTestView):
    def setup_method(self):
        super(TestSortFunctionsNoAttandanceView, self).setup_method()
        self.url = '/{}/functions/'
        self.view = views.sort_functions
        self.use_meeting = False

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied
        self.logged_in_protokollant = permission_denied
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super(TestSortFunctionsNoAttandanceView, self).prepare_variables()
        self.mt.attendance = False
        self.mt.save()

class TestSortFunctionsNoAttandanceFuncView(TestSortFunctionsNoAttandanceView):
    def prepare_variables(self):
        super(TestSortFunctionsNoAttandanceView, self).prepare_variables()
        self.mt.attendance_with_func = False
        self.mt.save()


class TestDeleteFunctionView(AbstractTestView):
    def setup_method(self):
        super(TestDeleteFunctionView, self).setup_method()
        self.url = '/{}/delfun/{}/'
        self.view = views.delete_function
        self.use_func = True
        self.redirect_url = '/{}/functions/'

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = redirect_to_url
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied
        self.logged_in_protokollant = permission_denied
        self.admin_public = redirect_to_url
        self.admin_not_public = redirect_to_url

    def prepare_variables(self):
        super(TestDeleteFunctionView, self).prepare_variables()
        self.mt.attendance = True
        self.mt.attendance_with_func = True
        self.mt.save()


class TestDeleteFunctionNoAttandanceView(AbstractTestView):
    def setup_method(self):
        super(TestDeleteFunctionNoAttandanceView, self).setup_method()
        self.url = '/{}/delfun/{}/'
        self.view = views.delete_function
        self.use_func = True

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied
        self.logged_in_protokollant = permission_denied
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super(TestDeleteFunctionNoAttandanceView, self).prepare_variables()
        self.mt.attendance = False
        self.mt.save()

class TestDeleteFunctionNoAttandanceFuncView(TestDeleteFunctionNoAttandanceView):
    def prepare_variables(self):
        super(TestDeleteFunctionNoAttandanceView, self).prepare_variables()
        self.mt.attendance_with_func = False
        self.mt.save()


class TestAddPersonView(AbstractTestView):
    def setup_method(self):
        super(TestAddPersonView, self).setup_method()
        self.url = '/{}/{}/addperson/'
        self.view = views.add_person

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
        super(TestAddPersonView, self).prepare_variables()
        self.mt.attendance = True
        self.mt.save()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestAddPersonNoProtokollantView(AbstractTestView):
    def setup_method(self):
        super(TestAddPersonNoProtokollantView, self).setup_method()
        self.url = '/{}/{}/addperson/'
        self.view = views.add_person

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
        super(TestAddPersonNoProtokollantView, self).prepare_variables()
        self.mt.attendance = True
        self.mt.save()
        self.meeting.protokollant = None
        self.meeting.save()


class TestAddPersonNotAllowedView(AbstractTestView):
    def setup_method(self):
        super(TestAddPersonNotAllowedView, self).setup_method()
        self.url = '/{}/{}/addperson/'
        self.view = views.add_person

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
        super(TestAddPersonNotAllowedView, self).prepare_variables()
        self.mt.attendance = False
        self.mt.save()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestAddPersonNANPView(AbstractTestView):
    def setup_method(self):
        super(TestAddPersonNANPView, self).setup_method()
        self.url = '/{}/{}/addperson/'
        self.view = views.add_person

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
        super(TestAddPersonNANPView, self).prepare_variables()
        self.mt.attendance = False
        self.mt.save()
        self.meeting.protokollant = None
        self.meeting.save()


class TestDeletePersonsView(AbstractTestView):
    def setup_method(self):
        super(TestDeletePersonsView, self).setup_method()
        self.url = '/{}/delpersons/'
        self.view = views.delete_persons
        self.use_meeting = False

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

    def prepare_variables(self):
        super(TestDeletePersonsView, self).prepare_variables()
        self.mt.attendance = True
        self.mt.save()


class TestDeletePersonsNoAttandanceView(AbstractTestView):
    def setup_method(self):
        super(TestDeletePersonsNoAttandanceView, self).setup_method()
        self.url = '/{}/delpersons/'
        self.view = views.delete_persons
        self.use_meeting = False

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied
        self.logged_in_protokollant = permission_denied
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super(TestDeletePersonsNoAttandanceView, self).prepare_variables()
        self.mt.attendance = False
        self.mt.save()


class TestDeletePersonView(AbstractTestView):
    def setup_method(self):
        super(TestDeletePersonView, self).setup_method()
        self.url = '/{}/delperson/{}/'
        self.view = views.delete_person
        self.use_person = True

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

    def prepare_variables(self):
        super(TestDeletePersonView, self).prepare_variables()
        self.mt.attendance = True
        self.mt.save()


class TestDeletePersonNoAttandanceView(AbstractTestView):
    def setup_method(self):
        super(TestDeletePersonNoAttandanceView, self).setup_method()
        self.url = '/{}/delperson/{}/'
        self.view = views.delete_person
        self.use_person = True

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = permission_denied
        self.logged_in_protokollant = permission_denied
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super(TestDeletePersonNoAttandanceView, self).prepare_variables()
        self.mt.attendance = False
        self.mt.save()
