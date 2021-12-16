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

from .. import views

# pylint: disable=too-many-instance-attributes
# pylint: disable=attribute-defined-outside-init
# pylint: disable=super-with-arguments


class TestAddAttendeesView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/addatt/{}/"
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
        super().prepare_variables()
        self.mt1.attendance = True
        self.mt1.save()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestAddAttendeesNoProtokollantView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/addatt/{}/"
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
        super().prepare_variables()
        self.mt1.attendance = True
        self.mt1.save()
        self.meeting.protokollant = None
        self.meeting.save()


class TestAddAttendeesNotAllowedView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/addatt/{}/"
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
        super().prepare_variables()
        self.mt1.attendance = False
        self.mt1.save()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestAddAttendeesNANPView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/addatt/{}/"
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
        super().prepare_variables()
        self.mt1.attendance = False
        self.mt1.save()
        self.meeting.protokollant = None
        self.meeting.save()


class TestEditAttendeeYYView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/editatt/{}/"
        self.view = views.edit_attendee
        self.use_attendee = True
        self.use_meeting = False

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
        self.mt1.attendance = True
        self.mt1.attendance_with_func = True
        self.mt1.save()


class TestEditAttendeeNoAttendanceView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/editatt/{}/"
        self.view = views.edit_attendee
        self.use_attendee = True
        self.use_meeting = False

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
        self.mt1.attendance = False
        self.mt1.save()


class TestEditAttendeeNoAttendanceFuncView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/editatt/{}/"
        self.view = views.edit_attendee
        self.use_attendee = True
        self.use_meeting = False

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
        self.mt1.attendance_with_func = False
        self.mt1.save()


class TestDeleteAttendeeView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/delatt/{}/"
        self.view = views.delete_attendee
        self.use_attendee = True
        self.use_meeting = False
        self.redirect_url = "/person/meeting/addatt/{}/"

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
        super().prepare_variables()
        self.mt1.attendance = True
        self.mt1.save()


class TestDeleteAttendeeNoAttendanceView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/delatt/{}/"
        self.view = views.delete_attendee
        self.use_attendee = True
        self.use_meeting = False

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
        self.mt1.attendance = False
        self.mt1.save()


class TestShowFunctionsView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/functions/manage/{}/"
        self.view = views.manage_functions
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
        super().prepare_variables()
        self.mt1.attendance = True
        self.mt1.attendance_with_func = True
        self.mt1.save()


class TestShowFunctionsNoAttandanceView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/functions/manage/{}/"
        self.view = views.manage_functions
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
        super().prepare_variables()
        self.mt1.attendance = False
        self.mt1.save()


class TestShowFunctionsNoAttandanceFuncView(TestShowFunctionsNoAttandanceView):
    def prepare_variables(self):
        super().prepare_variables()
        self.mt1.attendance_with_func = False
        self.mt1.save()


class TestSortFunctionsView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/functions/sort/{}/"
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
        super().prepare_variables()
        self.mt1.attendance = True
        self.mt1.attendance_with_func = True
        self.mt1.save()


class TestSortFunctionsNoAttandanceView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/functions/manage/{}/"
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
        super().prepare_variables()
        self.mt1.attendance = False
        self.mt1.save()


class TestSortFunctionsNoAttandanceFuncView(TestSortFunctionsNoAttandanceView):
    def prepare_variables(self):
        super().prepare_variables()
        self.mt1.attendance_with_func = False
        self.mt1.save()


class TestDeleteFunctionView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/functions/delete/{}/"
        self.view = views.delete_function
        self.use_func = True

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
        super().prepare_variables()
        self.mt1.attendance = True
        self.mt1.attendance_with_func = True
        self.mt1.save()


class TestDeleteFunctionNoAttandanceView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/functions/delete/{}/"
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
        super().prepare_variables()
        self.mt1.attendance = False
        self.mt1.save()


class TestDeleteFunctionNoAttandanceFuncView(TestDeleteFunctionNoAttandanceView):
    def prepare_variables(self):
        super().prepare_variables()
        self.mt1.attendance_with_func = False
        self.mt1.save()


class TestAddPersonView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/addperson/{}/"
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
        super().prepare_variables()
        self.mt1.attendance = True
        self.mt1.save()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestAddPersonNoProtokollantView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/addperson/{}/"
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
        super().prepare_variables()
        self.mt1.attendance = True
        self.mt1.save()
        self.meeting.protokollant = None
        self.meeting.save()


class TestAddPersonNotAllowedView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/addperson/{}/"
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
        super().prepare_variables()
        self.mt1.attendance = False
        self.mt1.save()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestAddPersonNANPView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/addperson/{}/"
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
        super().prepare_variables()
        self.mt1.attendance = False
        self.mt1.save()
        self.meeting.protokollant = None
        self.meeting.save()


class TestPersonsView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/list/{}/"
        self.view = views.list_persons
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
        super().prepare_variables()
        self.mt1.attendance = True
        self.mt1.save()


class TestPersonsNoAttandanceView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/list/{}/"
        self.view = views.list_persons
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
        super().prepare_variables()
        self.mt1.attendance = False
        self.mt1.save()


class TestDeletePersonView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/delete/{}/"
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
        super().prepare_variables()
        self.mt1.attendance = True
        self.mt1.save()


class TestDeletePersonNoAttandanceView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/delete/{}/"
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
        super().prepare_variables()
        self.mt1.attendance = False
        self.mt1.save()


class TestAddAttendeesWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/addatt/{}/"
        self.view = views.add_attendees

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied  # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = accessible  # TODO not_found
        self.logged_in_protokollant = accessible  # TODO not_found
        self.admin_public = accessible  # TODO not_found
        self.admin_not_public = accessible  # TODO not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.mt2.attendance = True
        self.mt2.save()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestAddAttendeesNoProtokollantWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/addatt/{}/"
        self.view = views.add_attendees

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied  # TODO not_found
        self.logged_in_with_admin_rights = permission_denied  # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = accessible  # TODO not_found
        self.logged_in_protokollant = accessible  # TODO not_found
        self.admin_public = accessible  # TODO not_found
        self.admin_not_public = accessible  # TODO not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.mt2.attendance = True
        self.mt2.save()
        self.meeting.protokollant = None
        self.meeting.save()


class TestAddAttendeesNotAllowedWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/addatt/{}/"
        self.view = views.add_attendees

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied  # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = not_found
        self.logged_in_protokollant = not_found
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.mt2.attendance = False
        self.mt2.save()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestAddAttendeesNANPWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/addatt/{}/"
        self.view = views.add_attendees

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied  # TODO not_found
        self.logged_in_with_admin_rights = permission_denied  # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = not_found
        self.logged_in_protokollant = not_found
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.mt2.attendance = False
        self.mt2.save()
        self.meeting.protokollant = None
        self.meeting.save()


class TestEditAttendeeYYWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/editatt/{}/"
        self.view = views.edit_attendee
        self.use_attendee = True
        self.use_meeting = False

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied  # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = accessible  # TODO not_found
        self.logged_in_protokollant = accessible  # TODO not_found
        self.admin_public = accessible  # TODO not_found
        self.admin_not_public = accessible  # TODO not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.mt2.attendance = True
        self.mt2.attendance_with_func = True
        self.mt2.save()


class TestEditAttendeeNoAttendanceWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/editatt/{}/"
        self.view = views.edit_attendee
        self.use_attendee = True
        self.use_meeting = False

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied  # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = not_found
        self.logged_in_protokollant = not_found
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.mt2.attendance = False
        self.mt2.save()


class TestEditAttendeeNoAttendanceFuncWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/editatt/{}/"
        self.view = views.edit_attendee
        self.use_attendee = True
        self.use_meeting = False

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied  # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = not_found
        self.logged_in_protokollant = not_found
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.mt2.attendance_with_func = False
        self.mt2.save()


class TestDeleteAttendeeWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/delatt/{}/"
        self.view = views.delete_attendee
        self.use_attendee = True
        self.use_meeting = False
        self.redirect_url = None

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied  # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = redirect_to_url  # TODO not_found
        self.logged_in_protokollant = redirect_to_url  # TODO not_found
        self.admin_public = redirect_to_url  # TODO not_found
        self.admin_not_public = redirect_to_url  # TODO not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.mt2.attendance = True
        self.mt2.save()


class TestDeleteAttendeeNoAttendanceWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/delatt/{}/"
        self.view = views.delete_attendee
        self.use_attendee = True
        self.use_meeting = False
        self.redirect_url = "/person/meeting/addatt/{}/"

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied  # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = not_found
        self.logged_in_protokollant = not_found
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.mt2.attendance = False
        self.mt2.save()


class TestAddPersonWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/addperson/{}/"
        self.view = views.add_person

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied  # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = accessible  # TODO not_found
        self.logged_in_protokollant = accessible  # TODO not_found
        self.admin_public = accessible  # TODO not_found
        self.admin_not_public = accessible  # TODO not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.mt2.attendance = True
        self.mt2.save()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestAddPersonNoProtokollantWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/addperson/{}/"
        self.view = views.add_person

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied  # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = accessible  # TODO not_found
        self.logged_in_protokollant = accessible  # TODO not_found
        self.admin_public = accessible  # TODO not_found
        self.admin_not_public = accessible  # TODO not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.mt2.attendance = True
        self.mt2.save()
        self.meeting.protokollant = None
        self.meeting.save()


class TestAddPersonNotAllowedWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/addperson/{}/"
        self.view = views.add_person

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied  # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = not_found
        self.logged_in_protokollant = not_found
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.mt2.attendance = False
        self.mt2.save()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestAddPersonNANPWrongMTView(AbstractTestWrongMTView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/addperson/{}/"
        self.view = views.add_person

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = permission_denied  # TODO not_found
        self.logged_in_without_rights = permission_denied
        self.logged_in_sitzungsleitung = not_found
        self.logged_in_protokollant = not_found
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_variables(self):
        super().prepare_variables()
        self.mt2.attendance = False
        self.mt2.save()
        self.meeting.protokollant = None
        self.meeting.save()


class TestAddAttendeesImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/addatt/{}/"
        self.view = views.add_attendees

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
        self.mt1.attendance = True
        self.mt1.save()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestAddAttendeesNoProtokollantImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/addatt/{}/"
        self.view = views.add_attendees

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
        self.mt1.attendance = True
        self.mt1.save()
        self.meeting.protokollant = None
        self.meeting.save()


class TestAddAttendeesNotAllowedImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/addatt/{}/"
        self.view = views.add_attendees

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
        self.mt1.attendance = False
        self.mt1.save()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestAddAttendeesNANPImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/addatt/{}/"
        self.view = views.add_attendees

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
        self.mt1.attendance = False
        self.mt1.save()
        self.meeting.protokollant = None
        self.meeting.save()


class TestEditAttendeeYYImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/editatt/{}/"
        self.view = views.edit_attendee
        self.use_attendee = True
        self.use_meeting = False

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
        self.mt1.attendance = True
        self.mt1.attendance_with_func = True
        self.mt1.save()


class TestEditAttendeeNoAttendanceImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/editatt/{}/"
        self.view = views.edit_attendee
        self.use_attendee = True
        self.use_meeting = False

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
        self.mt1.attendance = False
        self.mt1.save()


class TestEditAttendeeNoAttendanceFuncImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/editatt/{}/"
        self.view = views.edit_attendee
        self.use_attendee = True
        self.use_meeting = False

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
        self.mt1.attendance_with_func = False
        self.mt1.save()


class TestDeleteAttendeeImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/delatt/{}/"
        self.view = views.delete_attendee
        self.use_attendee = True
        self.use_meeting = False
        self.redirect_url = "/person/meeting/addatt/{}/"

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
        self.mt1.attendance = True
        self.mt1.save()


class TestDeleteAttendeeNoAttendanceImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/delatt/{}/"
        self.view = views.delete_attendee
        self.use_attendee = True
        self.use_meeting = False

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
        self.mt1.attendance = False
        self.mt1.save()


class TestAddPersonImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/addperson/{}/"
        self.view = views.add_person

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
        self.mt1.attendance = True
        self.mt1.save()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestAddPersonNoProtokollantImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/addperson/{}/"
        self.view = views.add_person

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
        self.mt1.attendance = True
        self.mt1.save()
        self.meeting.protokollant = None
        self.meeting.save()


class TestAddPersonNotAllowedImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/addperson/{}/"
        self.view = views.add_person

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
        self.mt1.attendance = False
        self.mt1.save()
        self.meeting.protokollant = self.other_user
        self.meeting.save()


class TestAddPersonNANPImportedView(AbstractTestImportedView):
    def setup_method(self):
        super().setup_method()
        self.url = "/person/meeting/addperson/{}/"
        self.view = views.add_person

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
        self.mt1.attendance = False
        self.mt1.save()
        self.meeting.protokollant = None
        self.meeting.save()
