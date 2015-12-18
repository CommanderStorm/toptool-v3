from django.db import models
from meetings.models import Meeting, MeetingType

class Top(models.Model):
    title = models.CharField(
        max_length=200,
    )

    author = models.CharField(
        max_length=50,
    )

    email = models.CharField(
        max_length=100,
    )

    description = models.TextField()

    meeting = models.ForeignKey(
        Meeting,
    )

    topid = models.IntegerField()

    time = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return "{0} ({1}, {2})".format(self.title, self.author, self.email)


class StandardTop(models.Model):
    title = models.CharField(
        max_length=200,
    )

    description = models.TextField()

    meetingtype = models.ForeignKey(
        MeetingType,
    )

    topid = models.IntegerField()

    def __str__(self):
        return "{0} ({1})".format(self.title, self.meetingtype)


