from django import forms
from django.contrib.auth.models import Group, User
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from toptool.forms import DualListField, UserDualListField

from .models import MeetingType

class MTBaseForm(forms.ModelForm):
    groups = DualListField(
        Group.objects.all().order_by('name'),
        required=False,
        label=_("Gruppen"),
    )
    users = UserDualListField(
        User.objects.all().order_by('first_name', 'last_name', 'username'),
        required=False,
        label=_("Benutzer"),
    )
    admin_groups = DualListField(
        Group.objects.all().order_by('name'),
        required=False,
        label=_("Admin-Gruppen"),
    )
    admin_users = UserDualListField(
        User.objects.all().order_by('first_name', 'last_name', 'username'),
        required=False,
        label=_("Admin-Benutzer"),
    )

    def __init__(self, *args, **kwargs):
        super(MTBaseForm, self).__init__(*args, **kwargs)
        if not settings.ETHERPAD_API_URL:
            self.fields['pad_setting'].widget = forms.HiddenInput()


class MTForm(MTBaseForm):
    class Meta:
        model = MeetingType
        exclude = ['id']


class MTAddForm(MTBaseForm):
    class Meta:
        model = MeetingType
        fields = "__all__"

