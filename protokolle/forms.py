from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db.models import Max
from django.template import defaultfilters

from toptool.forms import UserChoiceField

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
        meeting = kwargs.pop('meeting')
        users = kwargs.pop('users')
        sitzungsleitung = kwargs['initial']['sitzungsleitung']
        super(SitzungsleitungsForm, self).__init__(*args, **kwargs)

        self.fields['sitzungsleitung'].queryset = users
        if sitzungsleitung:
            self.fields['sitzungsleitung'].widget = forms.HiddenInput()

        if not protokoll_exists and not meeting.pad:
            self.fields['protokoll'].required = True


class ProtokollForm(SitzungsleitungsForm):
    class Meta:
        model = Protokoll
        exclude = ['meeting', 'version', 't2t']

    def __init__(self, *args, **kwargs):
        self.meeting = kwargs['meeting']
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

class TemplatesForm(forms.Form):
    source = forms.ChoiceField(
        widget=forms.RadioSelect(),
        label=_("Quelle"),
    )

    line_breaks = forms.ChoiceField(
        choices=(
            ("win", _("Windows-Zeilenumbrüche")),
            ("unix", _("Linux/Mac-Zeilenumbrüche")),
        ),
        widget=forms.RadioSelect(),
        label=_("Zeilenumbrüche"),
    )

    def __init__(self, *args, **kwargs):
        last_edit_pad = kwargs.pop('last_edit_pad')
        last_edit_file = kwargs.pop('last_edit_file')
        super(TemplatesForm, self).__init__(*args, **kwargs)

        choices = []
        if last_edit_file:
            choices.append(
                ('file', _("Quell-Datei des erstellten Protokolls (Stand: %(time)s)") %
                 {'time': defaultfilters.date(last_edit_file,
                                              "SHORT_DATETIME_FORMAT")})
            )
        if last_edit_pad:
            choices.append(
                ('pad', _("Text aus dem Pad (Stand: %(time)s)") %
                 {'time': defaultfilters.date(last_edit_pad,
                                              "SHORT_DATETIME_FORMAT")})
            )
        choices.append(('template', _("leere Vorlage")))
        self.fields['source'].choices = choices
