from django import forms
from django.contrib.auth.models import Group, User
from django.utils.translation import ugettext_lazy as _

from .models import MeetingType


class MTBaseForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        Group.objects.all(),
        required=False,
        label=_("Gruppen"),
    )
    users = forms.ModelMultipleChoiceField(
        User.objects.all(),
        required=False,
        label=_("Benutzer"),
    )
    admin_groups = forms.ModelMultipleChoiceField(
        Group.objects.all(),
        required=False,
        label=_("Admin-Gruppen"),
    )
    admin_users = forms.ModelMultipleChoiceField(
        User.objects.all(),
        required=False,
        label=_("Admin-Benutzer"),
    )


class MTForm(MTBaseForm):
    class Meta:
        model = MeetingType
        exclude = ['shortname']


class MTAddForm(MTBaseForm):
    class Meta:
        model = MeetingType
        fields = "__all__"
