import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _

from meetings.models import Meeting
from meetingtypes.models import MeetingType


class Top(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(
        _("Titel des TOPs"),
        max_length=200,
    )

    author = models.CharField(
        _("Dein Name"),
        max_length=50,
    )

    email = models.CharField(
        _("Deine E-Mailadresse"),
        max_length=100,
    )

    description = models.TextField(
        _("Kurze Beschreibung"),
        blank=True,
    )

    protokoll_templ = models.TextField(
        _("Protokoll-Template"),
        blank=True,
    )

    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        verbose_name=_("Sitzung"),
    )

    topid = models.IntegerField(
        _("TOP-Id"),
    )

    def __str__(self):
        if self.author and self.email:
            return "{0} ({1}, {2})".format(self.title, self.author, self.email)
        return self.title

    def protokoll_template(self):
        if self.protokoll_templ:
            return self.protokoll_templ
        else:
            return self.description


class StandardTop(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(
        _("Titel des TOPs"),
        max_length=200,
    )

    description = models.TextField(
        _("Kurze Beschreibung"),
        blank=True,
    )

    protokoll_templ = models.TextField(
        _("Protokoll-Template"),
        blank=True,
    )

    meetingtype = models.ForeignKey(
        MeetingType,
        on_delete=models.CASCADE,
        verbose_name=_("Sitzungsgruppe"),
    )

    topid = models.IntegerField(
        _("TOP-Id"),
    )

    def __str__(self):
        return "{0}. {1}".format(self.topid, self.title)
