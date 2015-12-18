from django.db import models

from meetings.models import Meeting

class Protokoll(models.Model):
    meeting = models.ForeignKey(
        Meeting,
    )

    time = models.DateTimeField()

    approved = models.BooleanField()

