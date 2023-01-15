import datetime

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Function(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(_("Amt"), max_length=200)
    plural = models.CharField(_("Amt im Plural"), max_length=200, blank=True)

    @property
    def protokollname(self):
        """
        Return the name for this function, which is shown in the protocol.
        """
        return self.plural or self.name

    sort_order = models.IntegerField(_("Index für Sortierung"))

    meetingtype = models.ForeignKey(
        "meetingtypes.MeetingType",
        on_delete=models.CASCADE,
        verbose_name=_("Sitzungsgruppe"),
    )

    def __str__(self) -> str:
        return self.name


class Person(models.Model):
    """
    The type person saves the name of a person who attended a meeting of the
    meeting type and his/her current functions.
    """

    meetingtype = models.ForeignKey(
        "meetingtypes.MeetingType",
        on_delete=models.CASCADE,
        verbose_name=_("Sitzungsgruppe"),
    )

    name = models.CharField(_("Name"), max_length=200)

    functions = models.ManyToManyField(Function, blank=True, verbose_name=_("Ämter"))

    @property
    def functions_string(self) -> str:
        """
        @return: pretty-format all functions
        """
        if self.functions.exists():
            concat_funcs = ", ".join(str(f) for f in self.functions.all())
            return f"({concat_funcs})"
        return ""

    version = models.DateTimeField(_("Zuletzt geaendert"), auto_now_add=True)
    last_selected = models.DateTimeField(_("Zuletzt anwesend"), auto_now_add=True)

    @property
    def not_selected_in_180_days(self) -> bool:
        """
        @return: if last_selected is older than 180 days
        """
        return self.last_selected < timezone.now() - datetime.timedelta(days=180)

    def __str__(self) -> str:
        if self.functions.exists():
            return f"{self.name} {self.functions_string}"
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

    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(_("Name"), max_length=200)

    person = models.ForeignKey(Person, blank=True, null=True, on_delete=models.SET_NULL, verbose_name=_("Person"))
    meeting = models.ForeignKey("meetings.Meeting", on_delete=models.CASCADE, verbose_name=_("Sitzung"))
    functions = models.ManyToManyField(Function, blank=True, verbose_name=_("Ämter"))

    @property
    def functions_string(self):
        """
        shortcut to pretty-format all functions of an attendee
        @return: the functions as string
        """
        if self.functions.exists():
            concat_funcs = ", ".join(str(f) for f in self.functions.all())
            return f"({concat_funcs})"
        return ""

    version = models.DateTimeField(_("Version"))

    def __str__(self) -> str:
        if self.functions.exists():
            return f"{self.name} {self.functions_string}"
        return self.name
