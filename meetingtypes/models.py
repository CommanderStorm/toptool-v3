import datetime

from django.db import models
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator
from django.conf import settings


class MeetingType(models.Model):
    ADMIN = "_admin"
    APP_NAME = "meetingtypes."

    name = models.CharField(
        _("Name"),
        max_length=200,
        unique=True,
    )

    id = models.CharField(
        _("URL-Kurzname"),
        max_length=20,
        validators=[
            RegexValidator(r'^[a-z]+$', _("Nur Buchstaben von a-z erlaubt!")),
            RegexValidator(
                r'^(admin|login|logout|overview|all|add|protokolle|static|profile)$',
                _("Name ist reserviert!"),
                inverse_match=True,
            ),
        ],
        primary_key=True,
    )

    mailinglist = models.EmailField(
        _("Mailingliste"),
    )

    # components settings
    ## general
    public = models.BooleanField(
        _("Sitzungsgruppe öffentlich zugänglich machen"),
    )
    ical_key = models.UUIDField(
        _("iCal-Key"),
        blank=True,
        null=True,
    )

    ## attendance
    attendance = models.BooleanField(
        _("Anwesenheitsliste verwenden"),
    )
    attendance_with_func = models.BooleanField(
        _("Ämter in Anwesenheitsliste verwenden"),
    )

    ## minutes
    protokoll = models.BooleanField(
        _("Protokoll verwenden"),
    )
    write_protokoll_button = models.BooleanField(
        _("Nicht-Admins können sich selbst zum Protokollanten machen"),
    )
    approve = models.BooleanField(
        _("Protokolle müssen genehmigt werden, bevor sie veröffentlicht werden"),
    )
    motion_tag = models.BooleanField(
        _("Kurze Syntax für Anträge im Protokoll verwenden"),
    )
    point_of_order_tag = models.BooleanField(
        _("Kurze Syntax für GO-Anträge im Protokoll verwenden"),
    )
    attachment_protokoll = models.BooleanField(
        _("Anhänge zum Protokoll ermöglichen"),
    )

    ## tops
    tops = models.BooleanField(
        _("Tagesordnung verwenden"),
    )
    TOP_PERMS = (
        ("admin", _("Nur Sitzungsgruppen-Admins und Sitzungsleitung können TOPs eintragen")),
        ("perm", _("Nur Benutzer mit Rechten für die Sitzungsgruppen können TOPs eintragen")),
        ("public", _("Alle, auch nicht eingeloggte Benutzer, können TOPs eintragen (nur relevant, wenn Sitzungsgruppe öffentlich ist)")),
    )
    top_perms = models.CharField(
        _("Rechte für das Eintragen von TOPs"),
        max_length=10,
        choices=TOP_PERMS,
        default="public",
    )
    top_deadline = models.BooleanField(
        _('Deadline zum Eintragen von TOPs verwenden'),
    )
    standard_tops = models.BooleanField(
        _('Standard-TOPs (TOPs, die für jede Sitzung automatisch erstellt werden) verwenden'),
    )
    other_in_tops = models.BooleanField(
        _('Am Ende der TOPs einen TOP "Sonstiges" standardmäßig hinzufügen'),
    )
    attachment_tops = models.BooleanField(
        _("Anhänge zu TOPs ermöglichen"),
    )

    pad_setting = models.BooleanField(
        _("Protokoll auch online schreiben (mit Etherpad)"),
    )

    first_topid = models.IntegerField(
        _("Nummer des ersten TOPs"),
        default=1,
    )

    def __str__(self):
        return self.name

    def permission(self):
        return MeetingType.APP_NAME + self.id

    def admin_permission(self):
        return MeetingType.APP_NAME + self.id + MeetingType.ADMIN

    def get_permission(self):
        content_type = ContentType.objects.get_for_model(MeetingType)
        codename = self.id
        return Permission.objects.get(
            content_type=content_type, codename=codename)

    def get_admin_permission(self):
        content_type = ContentType.objects.get_for_model(MeetingType)
        codename = self.id + MeetingType.ADMIN
        return Permission.objects.get(
            content_type=content_type, codename=codename)

    def past_meetings_by_year(self, year):
        return self.meeting_set.filter(time__lt=timezone.now()).filter(
            time__gte=timezone.make_aware(datetime.datetime(year, 1, 1)),
            time__lt=timezone.make_aware(datetime.datetime(year + 1, 1, 1)),
        )

    @property
    def upcoming_meetings(self):
        return self.meeting_set.filter(time__gte=timezone.now())

    @property
    def years(self):
        times = self.meeting_set.order_by('time').values_list('time',
            flat=True)
        years = list(set(map(lambda t: t.year, times)))
        years.sort()
        return years

    @property
    def last_meeting(self):
        return self.meeting_set.filter(time__lt=timezone.now()).latest('time')

    @property
    def next_meeting(self):
        return self.upcoming_meetings.earliest('time')

    @property
    def today(self):
        return self.meeting_set.filter(time__date=timezone.now().date())

    @property
    def tomorrow(self):
        return self.meeting_set.filter(
            time__date=timezone.now().date()+datetime.timedelta(days=1))

    @property
    def pad(self):
        return settings.ETHERPAD_API_URL and self.pad_setting


# delete permissions when meetingtype object is deleted
@receiver(pre_delete, sender=MeetingType)
def delete_protokoll(sender, **kwargs):
    instance = kwargs.get('instance')
    try:
        instance.get_permission().delete()
    except Permission.DoesNotExist:
        pass
    try:
        instance.get_admin_permission().delete()
    except Permission.DoesNotExist:
        pass
