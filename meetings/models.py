from django.db import models
from persons.models import Person
from django.core.mail import send_mail
from django.template.loader import get_template
from django.core.urlresolvers import reverse

class MeetingType(models.Model):
    name = models.CharField(
        max_length = 200,
    )

    shortname = models.CharField(
        max_length = 20,
    )

    mailinglist = models.CharField(
        max_length = 50,
    )

    approve = models.BooleanField()

    attendance = models.BooleanField()

    def __str__(self):
        return self.name


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
    # SET-Feedback-Treffen
    title = models.CharField(
        max_length = 200,
    )

    topdeadline = models.DateTimeField()

    sitzungsleitung = models.ForeignKey(
        Person,
        related_name = "sitzungsleitung",
    )

    protokollant = models.ForeignKey(
        Person,
        related_name = "protokollant",
    )

    attendees = models.ManyToManyField(
        Person,
        related_name = "attendees",
    )

    def __str__(self):
        return "{0} am {1} in {2}".format(self.title, self.time,
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


