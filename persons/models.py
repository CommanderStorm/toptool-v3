from django.db import models

from meetings.models import Meeting
from meetingtypes.models import MeetingType


class Function(models.Model):
    name = models.CharField(
        max_length = 200,
    )

    plural = models.CharField(
        max_length = 200,
        blank=True,
    )

    def __str__(self):
        return self.name


class Person(models.Model):
    """
    The type person saves the name of a person who attended a meeting of the
    meeting type and his/her current functions.
    """

    name = models.CharField(
        max_length = 200,
    )

    functions = models.ManyToManyField(
        Function,
        blank = True,
    )

    meetingtype = models.ForeignKey(
        MeetingType,
    )

    version = models.DateTimeField(
        auto_now=True,
    )
    
    def __str__(self):
        return "{0} ({1})".format(self.name, ', '.join(str(f) for
            f in self.functions.all()))


class Attendee(models.Model):
    """
    The type attendee saves a person who attended the given meeting
    together with his/her functions at that time.
    The separate type is used, because a function may change over time,
    but the name usually does not change.

    If the functions are changed and the self.version == self.person.version
    the change is propagated to the person type and both version attributes
    are updated to current time.
    If the versions do not match, only the self.functions are updated.
    """

    name = models.CharField(
        max_length = 200,
        blank=True,
    )

    person = models.ForeignKey(
        Person,
        blank=True,
        null=True,
    )

    meeting = models.ForeignKey(
        Meeting,
    )

    functions = models.ManyToManyField(
        Function,
        blank = True,
    )

    version = models.DateTimeField()

    def __str__(self):
        return "{0} ({1})".format(self.get_name(), ', '.join(str(f) for
            f in self.functions.all()))

    def get_name(self):
        if self.person:
            return self.person.name
        return self.name

