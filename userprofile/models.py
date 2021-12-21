import uuid

from django.contrib.auth.models import User  # pylint: disable=imported-auth-user
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from meetingtypes.models import MeetingType


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Benutzer"),
    )
    color = models.CharField(_("Farbe"), max_length=30, blank=True)

    CM_DARK = "dark"
    CM_LIGHT = "light"
    CM_CHOICES = (
        (CM_LIGHT, _("Hell")),
        (CM_DARK, _("Dunkel")),
    )
    colormode = models.CharField(
        _("Farbschema"),
        max_length=30,
        blank=True,
        default=CM_LIGHT,
        choices=CM_CHOICES,
    )

    ical_key = models.UUIDField(_("iCal-Key"), default=uuid.uuid4, unique=True)

    @property
    def darkmode(self):
        return self.colormode == self.CM_DARK

    def __str__(self):
        return str(self.user)


class MeetingTypePreference(models.Model):
    class Meta:
        unique_together = ("user", "meetingtype")

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Benutzer"),
    )
    meetingtype = models.ForeignKey(
        MeetingType,
        on_delete=models.CASCADE,
        verbose_name=_("Sitzungsgruppe"),
    )
    sortid = models.IntegerField(_("Sort-ID"))

    def __str__(self) -> str:
        return f"{self.user}-{self.meetingtype} (sortid {self.sortid})"


# pylint: disable=unused-argument
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


# pylint: enable=unused-argument
