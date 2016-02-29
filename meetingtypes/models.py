from django.db import models

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


