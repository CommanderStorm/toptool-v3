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

    description = models.TextField(
        blank=True,
    )
    
    protokoll_templ = models.TextField(
        blank=True,
    )

    meeting = models.ForeignKey(
        Meeting,
    )

    topid = models.IntegerField(
        unique=True,
    )

    time = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return "{0} ({1}, {2})".format(self.title, self.author, self.email)

    def protokoll_template(self):
        if self.protokoll_templ:
            return self.protokoll_templ
        else:
            return self.description


class StandardTop(models.Model):
    title = models.CharField(
        max_length=200,
    )

    description = models.TextField(
        blank=True,
    )

    protokoll_templ = models.TextField(
        blank=True,
    )

    meetingtype = models.ForeignKey(
        MeetingType,
    )

    topid = models.IntegerField(
        unique=True,
    )

    def __str__(self):
        return "{0}. {1}".format(self.topid, self.title)


