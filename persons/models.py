import uuid
import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from meetings.models import Meeting
from meetingtypes.models import MeetingType


class Function(models.Model):
    #id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(
        _("Amt"),
        max_length=200,
    )

    plural = models.CharField(
        _("Amt im Plural"),
        max_length=200,
        blank=True,
    )

    sort_order = models.IntegerField(
        _("Index für Sortierung"),
    )

    meetingtype = models.ForeignKey(
        MeetingType,
        on_delete=models.CASCADE,
        verbose_name=_("Sitzungsgruppe"),
    )

    def __str__(self):
        return self.name

    @property
    def protokollname(self):
        return self.plural or self.name


class Person(models.Model):
    """
    The type person saves the name of a person who attended a meeting of the
    meeting type and his/her current functions.
    """
    name = models.CharField(
        _("Name"),
        max_length=200,
    )

    functions = models.ManyToManyField(
        Function,
        blank=True,
        verbose_name=_("Aemter"),
    )

    meetingtype = models.ForeignKey(
        MeetingType,
        on_delete=models.CASCADE,
        verbose_name=_("Sitzungsgruppe"),
    )

    version = models.DateTimeField(
        _("Zuletzt geaendert"),
        auto_now_add=True,
    )

    last_selected = models.DateTimeField(
        _("Zuletzt anwesend"),
        auto_now_add=True,
    )

    def not_selected_in_180_days(self):
        return (self.last_selected < timezone.now() +
                datetime.timedelta(days=-180))

    def get_functions(self):
        if self.functions.exists():
            return "({0})".format(
                ', '.join(str(f) for f in self.functions.all()))
        return ""


    def __str__(self):
        if self.functions.exists():
            return "{0} {1}".format(
                self.name,
                self.get_functions())
        return self.name


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

    #id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(
        _("Name"),
        max_length=200,
    )

    person = models.ForeignKey(
        Person,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Person"),
    )

    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        verbose_name=_("Sitzung"),
    )

    functions = models.ManyToManyField(
        Function,
        blank=True,
        verbose_name=_("Aemter"),
    )

    version = models.DateTimeField(
        _("Version"),
    )

    def get_functions(self):
        if self.functions.exists():
            return "({0})".format(
                ', '.join(str(f) for f in self.functions.all()))
        return ""

    def __str__(self):
        if self.functions.exists():
            return "{0} {1}".format(
                self.name,
                self.get_functions())
        return self.name
