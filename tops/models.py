import uuid
import magic

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError

from meetings.models import Meeting
from meetingtypes.models import MeetingType


def attachment_path(instance, filename):
    # dir:      MEDIA_ROOT/attachments/<meetingtype.id>/
    # filename: top_<year_<month>_<day>_<topid>_<filname>
    return 'attachments/{0}/top_{1:04}_{2:02}_{3:02}_{4}_{5}'.format(
        instance.meeting.meetingtype.id,
        instance.meeting.time.year,
        instance.meeting.time.month,
        instance.meeting.time.day,
        instance.topid,
        filename,
    )


def validate_file_type(upload):
    filetype = magic.from_buffer(upload.file.read(1024), mime=True)
    if filetype not in settings.ALLOWED_FILE_TYPES:
        raise ValidationError(
            _('Der Dateityp wird nicht unterstützt. Es können nur PDFs ' \
                'hochgeladen werden'))


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

    email = models.EmailField(
        _("Deine E-Mailadresse"),
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

    attachment = models.FileField(
        _("Anhang"),
        upload_to=attachment_path,
        validators=[validate_file_type],
        blank=True,
        null=True,
    )

    def __str__(self):
        if self.author and self.email:
            return "{0} ({1}, {2})".format(self.title, self.author, self.email)
        return self.title


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
        return self.title
