from django.db import models
from persons.models import Person

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


