from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db.models import Max

from toptool_common.forms import UserChoiceField

from .models import Protokoll, Attachment


class SitzungsleitungsForm(forms.ModelForm):
    sitzungsleitung = UserChoiceField(
        queryset=None,
        label=_("Sitzungsleitung"),
    )
    protokoll = forms.FileField(
        label=_("Protokoll"),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        protokoll_exists = kwargs.pop('t2t')
        users = kwargs.pop('users')
        sitzungsleitung = kwargs['initial']['sitzungsleitung']
        super(SitzungsleitungsForm, self).__init__(*args, **kwargs)

        self.fields['sitzungsleitung'].queryset = users
        if sitzungsleitung:
            self.fields['sitzungsleitung'].widget = forms.HiddenInput()

        if not protokoll_exists:
            self.fields['protokoll'].required = True


class ProtokollForm(SitzungsleitungsForm):
    class Meta:
        model = Protokoll
        exclude = ['meeting', 'version', 't2t']

    def __init__(self, *args, **kwargs):
        self.meeting = kwargs.pop('meeting')
        self.t2t = kwargs['t2t']

        super(ProtokollForm, self).__init__(*args, **kwargs)

        if not self.meeting.meetingtype.approve:
            self.fields['approved'].widget = forms.HiddenInput()

    def save(self, commit=True):
        instance = super(ProtokollForm, self).save(False)

        instance.meeting = self.meeting
        instance.t2t = self.t2t

        if commit:
            instance.save()

        return instance


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        exclude = ['sort_order', 'meeting']

    def __init__(self, *args, **kwargs):
        self.meeting = kwargs.pop('meeting')

        super(AttachmentForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(AttachmentForm, self).save(False)

        instance.meeting = self.meeting
        if not instance.sort_order:
            maximum = self.meeting.attachment_set.aggregate(
                Max('sort_order'))["sort_order__max"]
            if maximum is None:
                maximum = -1
            instance.sort_order = maximum + 1

        if commit:
            instance.save()

        return instance
