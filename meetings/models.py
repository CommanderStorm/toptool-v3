import uuid
from typing import Any, Optional

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from toptool.utils.typing import AuthWSGIRequest
import tops.models
import protokolle.models

class Meeting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    meetingtype = models.ForeignKey(
        "meetingtypes.MeetingType",
        on_delete=models.CASCADE,
        verbose_name=_("Sitzungsgruppe"),
    )

    time = models.DateTimeField(_("Zeit"))
    room = models.CharField(_("Raum"), max_length=200, blank=True)
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

    # settings
    stdtops_created = models.BooleanField(_("Standard-TOPs wurden eingetragen"), default=False)
    imported = models.BooleanField(_("Importierte Sitzung"), default=False)

    pad = models.CharField(_("Pad-Name"), max_length=200, blank=True)

    def get_title(self) -> str:
        """
        @return: first_of(meeting.title, meetingtype.defaultmeetingtitle, meetingtype.name)
        """
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
        """
        @return: pretty-format the sitzungsleitung
        """
        if self.sitzungsleitung:
            return str(self.sitzungsleitung.get_full_name())
        if self.imported:
            return _("siehe Protokoll")
        return _("Keine Sitzungsleitung bestimmt")

    @property
    def min_takers_mail_joined(self) -> str:
        """
        @return: pretty-format/join all the e-mail addresses of the min_takers
        """
        min_takers = [minute_taker.email for minute_taker in self.minute_takers.all() if minute_taker.email]
        return ", ".join(min_takers) or _("Kein/e Protokollant/in bestimmt")

    @property
    def min_takers_str_protokill(self) -> str:
        """
        Refer to the Protokoll if imported, else pretty-format/join all the min_takers.
        This method should be used in protokoll, as referring to a protokol makes no sense here.
        @see Meeting.min_takers_str_html
        @return: string referring to min_takers
        """
        min_takers: list[str] = [minute_taker.get_full_name() for minute_taker in self.minute_takers.all()]
        return ", ".join(min_takers) or _("Kein/e Protokollant/in bestimmt")

    @property
    def min_takers_str_html(self):
        """
        Refer to the Protokoll if imported, else pretty-format/join all the min_takers.
        This method should be used in html, as refering to a protokol makes sense here.
        @see Meeting.min_takers_str_protokill
        @return: string referring to min_takers
        """
        if self.imported:
            return _("siehe Protokoll")
        return self.min_takers_str_protokill

    @property
    def previous(self):
        return self.meetingtype.meeting_set.filter(time__lt=self.time).latest("time")

    @property
    def next(self):
        return self.meetingtype.meeting_set.filter(time__gt=self.time).earliest("time")

    @property
    def tops_with_id(self) -> Optional[list[tuple[int, tops.models.Top]]]:
        if not self.meetingtype.tops:
            return None
        tops_list: list[tops.models.Top] = list(self.top_set.order_by("topid"))
        start_id = self.meetingtype.first_topid
        return [(counter + start_id, top) for counter, top in enumerate(tops_list)]

    @property
    def attachments_with_id(self) -> list[tuple[int, protokolle.models.Attachment]]:
        attachments: list[protokolle.models.Attachment] = list(self.attachment_set.order_by("sort_order"))
        return [(counter + 1, attachment) for counter, attachment in enumerate(attachments)]

    def meeting_url(self, request: AuthWSGIRequest) -> str:
        return request.build_absolute_uri(reverse("meetings:view_meeting", args=[self.id]))

    def get_tops_mail(self, request: AuthWSGIRequest) -> tuple[str, str, str, str]:
        # text from templates
        subject_template = get_template("meetings/mail/tops_mail_subject.txt")
        subject = subject_template.render({"meeting": self}).rstrip()

        text_template = get_template("meetings/mail/tops_mail.txt")
        mail_context = {
            "meeting": self,
            "tops_with_id": self.tops_with_id,
            "tops_url": self.meeting_url(request),
        }
        text = text_template.render(mail_context)

        from_email = f'"{request.user.get_full_name()}" <{request.user.email}>'
        to_email = f'"{self.meetingtype.name}" <{self.meetingtype.mailinglist}>'

        return subject, text, from_email, to_email

    def get_invitation_mail(self, request: AuthWSGIRequest) -> tuple[str, str, str, str]:
        # build urls
        add_tops_url = request.build_absolute_uri(reverse("tops:add_top", args=[self.id]))

        # text from templates
        subject_template = get_template("meetings/mail/invitation_mail_subject.txt")
        subject = subject_template.render({"meeting": self}).rstrip()

        text_template = get_template("meetings/mail/invitation_mail.txt")
        mail_context = {
            "meeting": self,
            "add_tops_url": add_tops_url,
            "details_url": self.meeting_url(request),
        }
        text = text_template.render(mail_context)

        from_email = f'"{request.user.get_full_name()}" <{request.user.email}>'
        to_email = f'"{self.meetingtype.name}" <{self.meetingtype.mailinglist}>'

        return subject, text, from_email, to_email

    def __str__(self) -> str:
        return _("%(title)s am %(date)s um %(time)s Uhr in %(room)s").format(
            {"title": self.get_title(), "date": self.time, "time": self.time, "room": self.room},
        )


# pylint: disable=unused-argument
@receiver(post_save, sender=Meeting)
def add_stdtops_listener(sender: type[Meeting], instance: Meeting, created: bool, **kwargs: Any) -> None:
    """
    Signal listener that adds stdtops when meeting is created.

    @param sender: the sender of the event
    @param instance: the Meeting
    @param created: if the meeting was newly created or just updated
    """

    if instance.stdtops_created:
        return  # meeting was only edited
    if not instance.meetingtype.tops:
        return

    if instance.meetingtype.standard_tops:
        stdtops = list(instance.meetingtype.standardtop_set.order_by("topid"))
        for i, stop in enumerate(stdtops):
            tops.models.Top.objects.create(
                title=stop.title,
                author="",
                email="",
                description=stop.description,
                protokoll_templ=stop.protokoll_templ,
                meeting=instance,
                topid=i + 1,
            )

    if instance.meetingtype.other_in_tops:
        tops.models.Top.objects.create(
            title="Sonstiges",
            author="",
            email="",
            meeting=instance,
            topid=10000,
        )

    instance.stdtops_created = True
    instance.save()


# pylint: enable=unused-argument
