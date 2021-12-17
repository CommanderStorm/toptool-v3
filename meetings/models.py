import uuid
from typing import List, Tuple

from django.contrib.auth import get_user_model
from django.db import models
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from tops.models import Top
from toptool.utils.typing import AuthWSGIRequest


class Meeting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    time = models.DateTimeField(_("Zeit"))
    room = models.CharField(_("Raum"), max_length=200, blank=True)
    meetingtype = models.ForeignKey(
        "meetingtypes.MeetingType",
        on_delete=models.CASCADE,
        verbose_name=_("Sitzungsgruppe"),
    )
    title = models.CharField(
        _("Alternativer Titel"),
        help_text=_(
            "Wenn kein Titel gesetzt ist, wird der Standardsitzungstitel "
            "oder der Name der Sitzungsgruppe verwendet.",
        ),
        max_length=200,
        blank=True,
    )
    topdeadline = models.DateTimeField(
        _("TOP-Einreichungsfrist"),
        help_text=_(
            "Frist, bis zu der TOPs eingereicht werden können. "
            "Wenn keine Frist gesetzt ist, können bis zum Beginn der Sitzung TOPs eingetragen werden.",
        ),
        blank=True,
        null=True,
    )
    sitzungsleitung = models.ForeignKey(
        get_user_model(),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="sitzungsleitung",
        verbose_name=_("Sitzungsleitung"),
    )

    minute_takers = models.ManyToManyField(
        get_user_model(),
        blank=True,
        verbose_name=_("Protokollant*in"),
    )

    stdtops_created = models.BooleanField(
        _("Standard-TOPs wurden eingetragen"),
        default=False,
    )

    imported = models.BooleanField(_("Importierte Sitzung"), default=False)

    pad = models.CharField(_("Pad-Name"), max_length=200, blank=True)

    # take title if set else use meeting type
    def get_title(self) -> str:
        return self.title or self.meetingtype.defaultmeetingtitle or self.meetingtype.name

    @property
    def topdeadline_over(self) -> bool:
        return (
            self.meetingtype.top_deadline
            and self.topdeadline
            and self.topdeadline < timezone.now()
            or self.time < timezone.now()
        )

    @property
    def sitzungsleitung_string(self):
        if self.sitzungsleitung:
            return str(self.sitzungsleitung.get_full_name())
        if self.imported:
            return _("siehe Protokoll")
        return _("Keine Sitzungsleitung bestimmt")

    def min_takers_joined(self) -> str:
        min_takers = []
        for minute_taker in self.minute_takers.all():
            min_takers.append(minute_taker.get_full_name())
        return ", ".join(min_takers)

    def min_takers_mail_joined(self) -> str:
        min_takers = [minute_taker.email for minute_taker in self.minute_takers.all() if minute_taker.email]
        return ", ".join(min_takers)

    @property
    def min_takers_string(self):
        if self.minute_takers.exists():
            return self.min_takers_joined()
        if self.imported:
            return _("siehe Protokoll")
        return _("Kein/e Protokollant/in bestimmt")

    @property
    def previous(self):
        return self.meetingtype.meeting_set.filter(time__lt=self.time).latest("time")

    @property
    def next(self):
        return self.meetingtype.meeting_set.filter(time__gt=self.time).earliest("time")

    def __str__(self) -> str:
        return _("%(title)s am %(date)s um %(time)s Uhr in %(room)s") % {
            "title": self.get_title(),
            "date": self.time,
            "time": self.time,
            "room": self.room,
        }

    def get_tops_with_id(self):
        if not self.meetingtype.tops:
            return None
        tops: List[Top] = list(self.top_set.order_by("topid"))
        start_id = self.meetingtype.first_topid
        for counter, top in enumerate(tops):
            top.get_topid = counter + start_id
        return tops

    def get_attachments_with_id(self):
        attachments = list(self.attachment_set.order_by("sort_order"))
        for counter, attachment in enumerate(attachments):
            attachment.get_attachmentid = counter + 1
        return attachments

    def get_tops_mail(self, request):
        # build url
        tops_url = request.build_absolute_uri(
            reverse("viewmeeting", args=[self.id]),
        )

        # get tops
        tops = self.get_tops_with_id()

        # text from templates
        subject_template = get_template("meetings/tops_mail_subject.txt")
        subject = subject_template.render({"meeting": self}).rstrip()

        text_template = get_template("meetings/tops_mail.txt")
        mail_context = {
            "meeting": self,
            "tops": tops,
            "tops_url": tops_url,
        }
        text = text_template.render(mail_context)

        from_email = f'"{request.user.get_full_name()}" <{request.user.email}>'
        to_email = f'"{self.meetingtype.name}" <{self.meetingtype.mailinglist}>'

        return subject, text, from_email, to_email

    def get_invitation_mail(
        self,
        request: AuthWSGIRequest,
    ) -> Tuple[str, str, str, str]:
        # build urls
        add_tops_url = request.build_absolute_uri(reverse("addtop", args=[self.id]))
        details_url = request.build_absolute_uri(reverse("viewmeeting", args=[self.id]))

        # text from templates
        subject_template = get_template("meetings/invitation_mail_subject.txt")
        subject = subject_template.render({"meeting": self}).rstrip()

        text_template = get_template("meetings/invitation_mail.txt")
        mail_context = {
            "meeting": self,
            "add_tops_url": add_tops_url,
            "details_url": details_url,
        }
        text = text_template.render(mail_context)

        from_email = f'"{request.user.get_full_name()}" <{request.user.email}>'
        to_email = f'"{self.meetingtype.name}" <{self.meetingtype.mailinglist}>'

        return subject, text, from_email, to_email
