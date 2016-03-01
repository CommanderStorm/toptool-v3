from django.db import models
from persons.models import Person
from meetingtypes.models import MeetingType
from django.core.mail import send_mail
from django.template.loader import get_template
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

class Meeting(models.Model):
    time = models.DateTimeField()

    room = models.CharField(
        max_length = 200,
    )

    semester = models.CharField(
        max_length = 200,
    )

    meetingtype = models.ForeignKey(
        MeetingType,
    )

    # for one meeting type there might be different meetings, e.g.
    # SET-Feedback-Treffen (the field is optional)
    title = models.CharField(
        max_length = 200,
        blank = True,
    )

    topdeadline = models.DateTimeField(
        blank = True,
        null = True,
    )

    sitzungsleitung = models.ForeignKey(
        User,
        blank = True,
        null = True,
        related_name = "sitzungsleitung",
    )

    protokollant = models.ForeignKey(
        User,
        blank = True,
        null = True,
        related_name = "protokollant",
    )

    attendees = models.ManyToManyField(
        Person,
        blank = True,
        related_name = "attendees",
    )

    # take title if set else use meeting type
    def get_title(self):
        return self.title or self.meetingtype.name

    def sl(self):
        return str(self.sitzungsleitung) or "No Sitzungsleitung"

    def pl(self):
        return str(self.protokollant) or "No Protokollant"

    def __str__(self):
        return "{0} am {1} in {2}".format(self.get_title(), self.time,
                self.room)

    def send_mail(self, request):
        # build url
        tops_url = request.build_absolute_uri(reverse('viewtops',
            args=[self.pk]))

        # get tops
        tops = self.top_set.order_by('topid')


        # text from templates
        subject_template = get_template('meetings/tops_mail_subject.txt')
        subject = subject_template.render({ 'meeting': self }).rstrip()

        text_template = get_template('meetings/tops_mail.txt')
        text = text_template.render({ 'meeting': self, 'tops': tops,
            'tops_url': tops_url })

        # send
        send_mail(subject, text, self.meetingtype.mailinglist,
                  [self.meetingtype.mailinglist], fail_silently=False)


