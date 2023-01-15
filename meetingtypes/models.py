import datetime
from contextlib import suppress
from typing import Any

from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.db.models import QuerySet
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import meetings.models


class MeetingType(models.Model):
    ADMIN = "_admin"
    APP_NAME = "meetingtypes."

    name = models.CharField(_("Name"), max_length=200, unique=True)

    id = models.CharField(
        _("URL-Kurzname"),
        max_length=20,
        validators=[
            RegexValidator(r"^[a-z]+$", _("Nur Buchstaben von a-z erlaubt!")),
            RegexValidator(
                r"^(admin|i18n|profile|meeting|meeting|protokoll|person|meetingtype|list|overview|"
                r"static|media|login|logout|oidc)$",
                _("Name ist reserviert!"),
                inverse_match=True,
            ),
            MinLengthValidator(2, _("Der URL-Kurzname muss mindestens 2 Buchstaben enthalten.")),
        ],
        primary_key=True,
    )

    mailinglist = models.EmailField(_("Mailingliste"), blank=True, null=True)

    defaultmeetingtitle = models.CharField(_("Standardsitzungstitel"), max_length=200, blank=True)

    # components settings
    # general
    public = models.BooleanField(_("Sitzungsgruppe öffentlich zugänglich machen"))
    ical_key = models.UUIDField(_("iCal-Key"), blank=True, null=True)

    # attendance
    attendance = models.BooleanField(_("Anwesenheitsliste verwenden"))
    attendance_with_func = models.BooleanField(_("Ämter in Anwesenheitsliste verwenden"))

    # minutes
    protokoll = models.BooleanField(_("Protokoll verwenden"))
    write_protokoll_button = models.BooleanField(_("Nicht-Admins können sich selbst zum Protokollanten machen"))
    approve = models.BooleanField(_("Protokolle müssen genehmigt werden, bevor sie veröffentlicht werden"))
    motion_tag = models.BooleanField(_("Kurze Syntax für Anträge im Protokoll verwenden"))
    point_of_order_tag = models.BooleanField(_("Kurze Syntax für GO-Anträge im Protokoll verwenden"))
    attachment_protokoll = models.BooleanField(_("Anhänge zum Protokoll ermöglichen"))
    pad_setting = models.BooleanField(_("Protokoll auch online schreiben (mit Etherpad)"))

    # tops
    tops = models.BooleanField(_("Tagesordnung verwenden"))
    TOP_PERMS = (
        (
            "admin",
            _("Nur Sitzungsgruppen-Admins und Sitzungsleitung können TOPs eintragen"),
        ),
        (
            "perm",
            _("Nur Benutzer mit Rechten für die Sitzungsgruppen können TOPs eintragen"),
        ),
        (
            "public",
            _(
                "Alle, auch nicht eingeloggte Benutzer, können TOPs eintragen "
                "(nur relevant, wenn Sitzungsgruppe öffentlich ist)",
            ),
        ),
    )
    top_perms = models.CharField(
        _("Rechte für das Eintragen von TOPs"),
        max_length=10,
        choices=TOP_PERMS,
        default="public",
    )
    top_user_edit = models.BooleanField(_("Benutzer dürfen ihre eigenen TOPs bearbeiten/löschen"))
    top_deadline = models.BooleanField(_("Deadline zum Eintragen von TOPs verwenden"))
    standard_tops = models.BooleanField(
        _("Standard-TOPs (TOPs, die für jede Sitzung automatisch erstellt werden) verwenden"),
    )
    other_in_tops = models.BooleanField(_('Am Ende der TOPs einen TOP "Sonstiges" standardmäßig hinzufügen'))
    attachment_tops = models.BooleanField(_("Anhänge zu TOPs ermöglichen"))
    anonymous_tops = models.BooleanField(_("Anonyme TOPs (ohne Name und E-Mail-Adresse) ermöglichen"))
    first_topid = models.IntegerField(_("Nummer des ersten TOPs"), default=1)
    custom_template = models.CharField(
        _("Angepasstes Template"),
        max_length=100,
        blank=True,
        help_text=_("Wenn keines angegeben ist, wird das Standard-Template verwendet."),
    )

    def __str__(self) -> str:
        return self.name

    def permission(self) -> str:
        """@return: the permission id needed to access this meeting type."""
        return MeetingType.APP_NAME + self.id

    def admin_permission(self) -> str:
        """@return: the permission id for the admin permission to this meeting type."""
        return MeetingType.APP_NAME + self.id + MeetingType.ADMIN

    def get_permission(self) -> Permission:
        """
        @return: the permission needed to access this meeting type.
        """
        content_type: ContentType = ContentType.objects.get_for_model(MeetingType)
        codename: str = self.id
        return Permission.objects.get(content_type=content_type, codename=codename)

    def get_admin_permission(self) -> Permission:
        """
        @return: the permission needed to administrate this meeting type.
        """
        content_type = ContentType.objects.get_for_model(MeetingType)
        codename = self.id + MeetingType.ADMIN
        return Permission.objects.get(
            content_type=content_type,
            codename=codename,
        )

    def past_meetings_by_year(
        self,
        year: int,
        reverse_order: bool = False,
    ) -> QuerySet[meetings.models.Meeting]:
        """
        Returns all past meetings of this meeting type in the given year.
        Future meetings are not included.

        @param year: the year that should be filtered
        @param reverse_order: if True, the meetings are ordered by start date descending
        @return: all meetings of this meeting type in the given year
        """
        past_meetings = self.meeting_set.filter(time__lt=timezone.now())
        # restrict to the given year
        restricted_meetings = past_meetings.filter(
            time__gte=timezone.make_aware(datetime.datetime(year, 1, 1)),
            time__lt=timezone.make_aware(datetime.datetime(year + 1, 1, 1)),
        )
        if reverse_order:
            return restricted_meetings.order_by("-time")
        return restricted_meetings.order_by("time")

    @property
    def upcoming_meetings(self) -> QuerySet[meetings.models.Meeting]:
        """
        Returns all upcoming meetings of this meeting type.
        @return: a queryset of meetings
        """
        return self.meeting_set.filter(time__gte=timezone.now()).order_by("time")

    @property
    def years(self) -> list[int]:
        """
        Returns all years in which there are meetings of this meeting type.
        @return: a list of years
        """
        return list(
            self.meeting_set.values_list("time__year", flat=True).order_by("time__year").distinct(),
        )

    @property
    def last_meeting(self) -> meetings.models.Meeting:
        """
        Returns the last (least far lying in the past) meeting of this meeting type.
        @return: a meeting
        """
        return self.meeting_set.filter(time__lt=timezone.now()).latest("time")

    @property
    def next_meeting(self) -> meetings.models.Meeting:
        """
        Returns the next (least far lying in the future) meeting of this meeting type.
        @return: a meeting
        """
        return self.upcoming_meetings.earliest("time")

    @property
    def today(self) -> QuerySet[meetings.models.Meeting]:
        """
        Returns the all meetings of this meeting type that are happening today.
        @return: al matching meetings
        """
        return self.meeting_set.filter(time__date=timezone.now().date())

    @property
    def tomorrow(self) -> QuerySet[meetings.models.Meeting]:
        """
        Returns the all meetings of this meeting type that are happening tomorrow.
        @return: al matching meetings
        """
        date_tomorrow = timezone.now().date() + datetime.timedelta(days=1)
        return self.meeting_set.filter(time__date=date_tomorrow)

    @property
    def pad(self) -> bool:
        """
        Returns True if a pad is allowed and usable for this meeting type.
        @return: boolean
        """
        return self.pad_setting and bool(settings.ETHERPAD_API_URL)

    @property
    def send_tops_enabled(self) -> bool:
        """
        Returns True if tops are allowed and can be sent via mail for this meeting type.
        @return: boolean
        """
        return self.tops and bool(self.mailinglist)

    @property
    def send_invitation_enabled(self) -> bool:
        """
        Returns True if inviations can be sent via mail for this meeting type.
        @return:
        """
        return bool(self.mailinglist)

    @property
    def send_minutes_enabled(self) -> bool:
        """
        Returns True if minutes are allowed and can be sent via mail for this meeting type.
        @return: boolean
        """
        return self.protokoll and bool(self.mailinglist)

    @property
    def email_sending_enabled(self) -> bool:
        """
        Returns True if tops,invitations and minutes can be sent via mail for this meeting type.
        @return: boolean
        """
        return self.send_tops_enabled or self.send_invitation_enabled or self.send_minutes_enabled


# pylint: disable=unused-argument
@receiver(pre_delete, sender=MeetingType)
def delete_protokoll(sender: type[MeetingType], instance: MeetingType, **kwargs: Any) -> None:
    """
    Signal listener that delete permissions when meetingtype object is deleted.

    @param sender: the sender of the event
    @param instance: the MeetingType
    """
    with suppress(Permission.DoesNotExist):
        instance.get_permission().delete()
    with suppress(Permission.DoesNotExist):
        instance.get_admin_permission().delete()


# pylint: enable=unused-argument
