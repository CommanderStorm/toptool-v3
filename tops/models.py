import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from meetings.models import Meeting
from meetingtypes.models import MeetingType
from toptool.shortcuts import validate_file_type


class AttachmentStorage(FileSystemStorage):
    def url(self, name):
        top = Top.objects.get(attachment=name)
        return reverse(
            "showattachment",
            args=[
                top.meeting.meetingtype.id,
                top.meeting.id,
                top.id,
            ],
        )


def attachment_path(instance, filename):
    # dir:      MEDIA_ROOT/attachments/<meetingtype.id>/
    # filename: top_<year>_<month>_<day>_<topid>_<filname>
    return (
        f"attachments/{instance.meeting.meetingtype.id}/"
        f"top_{instance.meeting.time.year:04}_{instance.meeting.time.month:02}_"
        f"{instance.meeting.time.day:02}_{instance.topid}_{filename}"
    )


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
        storage=AttachmentStorage(),
        help_text=_("Erlaubte Dateiformate: %(filetypes)s")
        % {
            "filetypes": ", ".join(settings.ALLOWED_FILE_TYPES.keys()),
        },
        blank=True,
        null=True,
    )

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        verbose_name=_("Benutzer"),
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        if self.author and self.email:
            return f"{self.title} ({self.author}, {self.email})"
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

    def __str__(self) -> str:
        return self.title
