import uuid

from django.contrib.auth.models import User  # pylint: disable=imported-auth-user
from django.core.validators import RegexValidator
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
    C_DEFAULT = "#337ab7"
    color = models.CharField(
        _("Farbe"),
        validators=[RegexValidator(r"^#[0-9a-fA-F]{6}$", _("Nur valide Hex-Farbcodes sind erlaubt"))],
        max_length=30,
        default=C_DEFAULT,
    )

    CM_DARK = "dark"
    CM_LIGHT = "light"
    CM_CHOICES = (
        (CM_LIGHT, _("Hell")),
        (CM_DARK, _("Dunkel")),
    )
    colormode = models.CharField(
        _("Farbschema"),
        max_length=30,
        default=CM_LIGHT,
        choices=CM_CHOICES,
    )

    ical_key = models.UUIDField(_("iCal-Key"), default=uuid.uuid4, unique=True)

    @property
    def darkmode(self):
        return self.colormode == self.CM_DARK

    @property
    def contrast_hex(self):
        return self.get_contrasting_hex(self.color)

    @property
    def contrast(self):
        if self.requires_dark_contrast(self.color):
            return "dark"
        return "light"

    @property
    def contrast_inv(self):
        if not self.requires_dark_contrast(self.color):
            return "dark"
        return "light"

    @classmethod
    def requires_dark_contrast(cls, color):
        color = color.replace("#", "")
        red, green, blue = tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))
        contrast_score = red * 0.299 + green * 0.587 + blue * 0.114
        return contrast_score > 160

    @classmethod
    def get_contrasting_hex(cls, color: str) -> str:
        if cls.requires_dark_contrast(color):
            return "#000000"
        return "#ffffff"

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
