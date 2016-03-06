import uuid

from django.db import models
from django.core.mail import send_mail
from django.template.loader import get_template
from django.core.urlresolvers import reverse
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
        max_length=200,
        blank=True,
    )

    topdeadline = models.DateTimeField(
        _("TOP-Einreichungsfrist"),
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

    # take title if set else use meeting type
    def get_title(self):
        return self.title or self.meetingtype.name

    @property
    def topdeadline_over(self):
        return (self.topdeadline and self.topdeadline < timezone.now() or
                self.time < timezone.now())

    @property
    def sl(self):
        if self.sitzungsleitung:
            return str(self.sitzungsleitung.get_full_name())
        else:
            return _("Keine Sitzungsleitung bestimmt")

    @property
    def pl(self):
        if self.protokollant:
            return str(self.protokollant.get_full_name())
        else:
            return _("Kein/e Protokollant/in bestimmt")

    def __str__(self):
        return _("%(title)s am %(date)s um %(time)s Uhr in %(room)s") % {
            'title': self.get_title(),
            'date': self.time,
            'time': self.time,
            'room': self.room,
        }

    def send_tops(self, request):
        # build url
        tops_url = request.build_absolute_uri(
            reverse('viewmeeting', args=[self.pk]))

        # get tops
        tops = self.top_set.order_by('topid')

        # text from templates
        subject_template = get_template('meetings/tops_mail_subject.txt')
        subject = subject_template.render({'meeting': self}).rstrip()

        text_template = get_template('meetings/tops_mail.txt')
        text = text_template.render({'meeting': self, 'tops': tops,
                                     'tops_url': tops_url})

        # send
        send_mail(subject, text, self.meetingtype.mailinglist,
                  [self.meetingtype.mailinglist], fail_silently=False)

    def send_invitation(self, request):
        # build urls
        add_tops_url = request.build_absolute_uri(
            reverse('addtop', args=[self.pk]))
        details_url = request.build_absolute_uri(
            reverse('viewmeeting', args=[self.pk]))

        # text from templates
        subject_template = get_template('meetings/invitation_mail_subject.txt')
        subject = subject_template.render({'meeting': self}).rstrip()

        text_template = get_template('meetings/invitation_mail.txt')
        text = text_template.render({
            'meeting': self,
            'add_tops_url': add_tops_url,
            'details_url': details_url,
        })

        # send
        send_mail(subject, text, self.meetingtype.mailinglist,
                  [self.meetingtype.mailinglist], fail_silently=False)
