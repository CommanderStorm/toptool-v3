from django.db import models
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _


class MeetingType(models.Model):
    ADMIN = "_admin"
    APP_NAME = "meetingtypes."

    name = models.CharField(
        _("Name"),
        max_length=200,
        unique=True,
    )

    shortname = models.CharField(
        _("Kurzname"),
        max_length=20,
        unique=True,
    )

    mailinglist = models.CharField(
        _("Mailingliste"),
        max_length=50,
    )

    approve = models.BooleanField(
        _("Protokolle müssen genehmigt werden"),
    )

    attendance = models.BooleanField(
        _("Anwesenheitsliste"),
    )

    attendance_with_func = models.BooleanField(
        _("Anwesenheitslist mit Ämtern"),
    )

    public = models.BooleanField(
        _("Sitzungsgruppe ist öffentlich"),
    )

    other_in_tops = models.BooleanField(
        _('TOP "Sonstiges" standardmäßig hinzufügen'),
    )

    def __str__(self):
        return self.name

    def permission(self):
        return MeetingType.APP_NAME + self.shortname

    def admin_permission(self):
        return MeetingType.APP_NAME + self.shortname + MeetingType.ADMIN

    def get_permission(self):
        content_type = ContentType.objects.get_for_model(MeetingType)
        codename = self.shortname
        return Permission.objects.get(
            content_type=content_type, codename=codename)

    def get_admin_permission(self):
        content_type = ContentType.objects.get_for_model(MeetingType)
        codename = self.shortname + MeetingType.ADMIN
        return Permission.objects.get(
            content_type=content_type, codename=codename)

    @property
    def past_meetings(self):
        return self.meeting_set.filter(time__lt=timezone.now())

    @property
    def upcoming_meetings(self):
        return self.meeting_set.filter(time__gte=timezone.now())

    @property
    def last_meeting(self):
        return self.past_meetings.latest('time')

    @property
    def next_meeting(self):
        return self.upcoming_meetings.earliest('time')


# delete permissions when meetingtype object is deleted
@receiver(pre_delete, sender=MeetingType)
def delete_protokoll(sender, **kwargs):
    instance = kwargs.get('instance')
    instance.get_permission().delete()
    instance.get_admin_permission().delete()
