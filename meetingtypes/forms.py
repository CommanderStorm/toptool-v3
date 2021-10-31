import uuid

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from toptool.forms import DualListField, UserDualListField

from .models import MeetingType


class MTBaseForm(forms.ModelForm):
    groups = DualListField(
        Group.objects.all().order_by("name"),
        required=False,
        label=_("Gruppen"),
    )
    users = UserDualListField(
        get_user_model().objects.all().order_by("first_name", "last_name", "username"),
        required=False,
        label=_("Benutzer"),
    )
    admin_groups = DualListField(
        Group.objects.all().order_by("name"),
        required=False,
        label=_("Admin-Gruppen"),
    )
    admin_users = UserDualListField(
        get_user_model().objects.all().order_by("first_name", "last_name", "username"),
        required=False,
        label=_("Admin-Benutzer"),
    )
    ical = forms.BooleanField(
        label=_("Sitzungen als iCal-Abo veröffentlichen"),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not settings.ETHERPAD_API_URL:
            self.fields["pad_setting"].widget = forms.HiddenInput()
        if "instance" in kwargs and kwargs["instance"].ical_key:
            self.fields["ical"].initial = True

    def save(self, commit=True):
        instance = super().save(False)
        if self.cleaned_data["ical"]:
            if not instance.ical_key:
                instance.ical_key = uuid.uuid4()
        else:
            instance.ical_key = None
        if commit:
            instance.save()
        return instance


class MTForm(MTBaseForm):
    class Meta:
        model = MeetingType
        exclude = ["id", "ical_key", "custom_template"]


class MTAddForm(MTBaseForm):
    class Meta:
        model = MeetingType
        exclude = ["ical_key", "custom_template"]
