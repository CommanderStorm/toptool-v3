import datetime

from django.db import models
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator


class MeetingType(models.Model):
    ADMIN = "_admin"
    APP_NAME = "meetingtypes."

    name = models.CharField(
        _("Name"),
        max_length=200,
        unique=True,
    )

    id = models.CharField(
        _("Kurzname"),
        max_length=20,
        validators=[RegexValidator(r'^[a-z]+$',
                                   _("Nur Buchstaben von a-z erlaubt!"))],
        primary_key=True,
    )

    mailinglist = models.EmailField(
        _("Mailingliste"),
    )

    approve = models.BooleanField(
        _("Protokolle muessen genehmigt werden"),
    )

    attendance = models.BooleanField(
        _("Anwesenheitsliste"),
    )

    attendance_with_func = models.BooleanField(
        _("Anwesenheitslist mit Aemtern"),
    )

    public = models.BooleanField(
        _("Sitzungsgruppe ist oeffentlich"),
    )

    other_in_tops = models.BooleanField(
        _('TOP "Sonstiges" standardmaessig hinzufuegen'),
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


# delete permissions when meetingtype object is deleted
@receiver(pre_delete, sender=MeetingType)
def delete_protokoll(sender, **kwargs):
    instance = kwargs.get('instance')
    instance.get_permission().delete()
    instance.get_admin_permission().delete()
