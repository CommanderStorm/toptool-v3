import uuid

from django.db import models
from django.template.loader import get_template
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from meetingtypes.models import MeetingType


class Meeting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    time = models.DateTimeField(
        _("Zeit"),
    )

    room = models.CharField(
        _("Raum"),
        max_length=200,
        blank=True,
    )

    meetingtype = models.ForeignKey(
        MeetingType,
        on_delete=models.CASCADE,
        verbose_name=_("Sitzungsgruppe"),
    )

    # for one meeting type there might be different meetings, e.g.
    # SET-Feedback-Treffen (the field is optional)
    title = models.CharField(
        _("Alternativer Titel"),
        help_text=_("Wenn kein Titel gesetzt ist, wird der Name der Sitzungsgruppe verwendet."),
        max_length=200,
        blank=True,
    )

    topdeadline = models.DateTimeField(
        _("TOP-Einreichungsfrist"),
        help_text=_(
            "Frist, bis zu der TOPs eingereicht werden können. "
            "Wenn keine Frist gesetzt ist, können bis zum Beginn der Sitzung "
            "TOPs eingetragen werden."
        ),
        blank=True,
        null=True,
    )

    sitzungsleitung = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="sitzungsleitung",
        verbose_name=_("Sitzungsleitung"),
    )

    protokollant = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="protokollant",
        verbose_name=_("Protokollant/in"),
    )

    stdtops_created = models.BooleanField(
        _("Standard-TOPs wurden eingetragen"),
        default=False,
    )

    imported = models.BooleanField(
        _("Importierte Sitzung"),
        default=False,
    )

    pad = models.CharField(
        _("Pad-Name"),
        max_length=200,
        blank=True,
    )


    # take title if set else use meeting type
    def get_title(self):
        return self.title or self.meetingtype.name

    @property
    def topdeadline_over(self):
        return (self.meetingtype.top_deadline and self.topdeadline
                and self.topdeadline < timezone.now() or
                self.time < timezone.now())

    @property
    def sl(self):
        if self.sitzungsleitung:
            return str(self.sitzungsleitung.get_full_name())
        elif self.imported:
            return _("siehe Protokoll")
        else:
            return _("Keine Sitzungsleitung bestimmt")

    @property
    def pl(self):
        if self.protokollant:
            return str(self.protokollant.get_full_name())
        elif self.imported:
            return _("siehe Protokoll")
        else:
            return _("Kein/e Protokollant/in bestimmt")

    @property
    def previous(self):
        return self.meetingtype.meeting_set.filter(time__lt=self.time
            ).latest('time')

    @property
    def next(self):
        return self.meetingtype.meeting_set.filter(time__gt=self.time
            ).earliest('time')

    def __str__(self):
        return _("%(title)s am %(date)s um %(time)s Uhr in %(room)s") % {
            'title': self.get_title(),
            'date': self.time,
            'time': self.time,
            'room': self.room,
        }

    def get_tops_with_id(self):
        if not self.meetingtype.tops:
            return None
        tops = list(self.top_set.order_by('topid'))
        start_id = self.meetingtype.first_topid
        for i, t in enumerate(tops):
            t.get_topid = i + start_id
        return tops

    def get_attachments_with_id(self):
        attachments = list(self.attachment_set.order_by('sort_order'))
        for i, a in enumerate(attachments):
            a.get_attachmentid = i + 1
        return attachments

    def get_tops_mail(self, request):
        # build url
        tops_url = request.build_absolute_uri(
            reverse('viewmeeting', args=[self.meetingtype.id, self.id]))

        # get tops
        tops = self.get_tops_with_id()

        # text from templates
        subject_template = get_template('meetings/tops_mail_subject.txt')
        subject = subject_template.render({'meeting': self}).rstrip()

        text_template = get_template('meetings/tops_mail.txt')
        text = text_template.render({'meeting': self, 'tops': tops,
                                     'tops_url': tops_url})

        from_email = '"{0}" <{1}>'.format(
            request.user.get_full_name(),
            request.user.email,
        )

        to_email = '"{0}" <{1}>'.format(
            self.meetingtype.name,
            self.meetingtype.mailinglist,
        )

        return (subject, text, from_email, to_email)

    def get_invitation_mail(self, request):
        # build urls
        add_tops_url = request.build_absolute_uri(
            reverse('addtop', args=[self.meetingtype.id, self.id]))
        details_url = request.build_absolute_uri(
            reverse('viewmeeting', args=[self.meetingtype.id, self.id]))

        # text from templates
        subject_template = get_template('meetings/invitation_mail_subject.txt')
        subject = subject_template.render({'meeting': self}).rstrip()

        text_template = get_template('meetings/invitation_mail.txt')
        text = text_template.render({
            'meeting': self,
            'add_tops_url': add_tops_url,
            'details_url': details_url,
        })

        from_email = '"{0}" <{1}>'.format(
            request.user.get_full_name(),
            request.user.email,
        )

        to_email = '"{0}" <{1}>'.format(
            self.meetingtype.name,
            self.meetingtype.mailinglist,
        )

        return (subject, text, from_email, to_email)
