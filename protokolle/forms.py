from django import forms
from django.db.models import Max
from django.template import defaultfilters
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

from toptool.forms import UserChoiceField
from .models import Protokoll, Attachment


class ProtokollForm(forms.ModelForm):
    class Meta:
        model = Protokoll
        fields = (
            "source", "protokoll", "sitzungsleitung", "begin", "end", "approved"
        )

    source = forms.ChoiceField(
        widget=forms.RadioSelect(),
        label=_("Quelle"),
    )
    protokoll = forms.FileField(
        label=_("Protokoll"),
        help_text=_("Nur relevant, wenn 'Datei hochladen...' ausgewählt ist"),
        required=False,
    )
    sitzungsleitung = UserChoiceField(
        queryset=None,
        label=_("Sitzungsleitung"),
    )

    def __init__(self, *args, **kwargs):
        self.t2t = kwargs.pop('t2t')
        self.meeting = kwargs.pop('meeting')
        users = kwargs.pop('users')
        sitzungsleitung = kwargs['initial']['sitzungsleitung']
        last_edit_pad = kwargs.pop('last_edit_pad')
        last_edit_file = kwargs.pop('last_edit_file')
        super(ProtokollForm, self).__init__(*args, **kwargs)

        self.fields['sitzungsleitung'].queryset = users
        if sitzungsleitung:
            self.fields['sitzungsleitung'].widget = forms.HiddenInput()
        if not last_edit_pad and not last_edit_file:
            self.fields['protokoll'].required = True
            self.fields['protokoll'].help_text = ""
        if not self.meeting.meetingtype.approve:
            self.fields['approved'].widget = forms.HiddenInput()

        choices = []
        choices.append(('upload', _("Datei hochladen...")))
        if last_edit_pad:
            choices.append(
                ('pad', _("Text aus dem Pad (Stand: %(time)s)") %
                 {'time': defaultfilters.date(last_edit_pad,
                                              "SHORT_DATETIME_FORMAT")})
            )
        if last_edit_file:
            choices.append(
                ('file', _("Quell-Datei des erstellten Protokolls beibehalten (Stand: %(time)s)") %
                 {'time': defaultfilters.date(last_edit_file,
                                              "SHORT_DATETIME_FORMAT")})
            )
        self.fields['source'].choices = choices
        self.fields['begin'].input_formats = [
            '%H:%M',
            '%I:%M %p',
        ]
        self.fields['begin'].widget.format = (
            '%I:%M %p'
            if get_language() == 'en'
            else '%H:%M'
        )
        self.fields['end'].input_formats = [
            '%H:%M',
            '%I:%M %p',
        ]
        self.fields['end'].widget.format = (
            '%I:%M %p'
            if get_language() == 'en'
            else '%H:%M'
        )

    def clean(self):
        super(ProtokollForm, self).clean()
        if self.cleaned_data.get('source') == 'upload':
            if not self.cleaned_data.get('protokoll'):
                self.add_error(
                    "protokoll", forms.ValidationError(
                        _("Es wurde keine Datei hochgeladen."))
                )

    def save(self, commit=True):
        instance = super(ProtokollForm, self).save(False)

        instance.meeting = self.meeting
        instance.t2t = self.t2t
        instance.published = False

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


class PadForm(forms.Form):
    source = forms.ChoiceField(
        widget=forms.RadioSelect(),
        label=_("Quelle"),
    )

    template_file = forms.FileField(
        label=_("Datei"),
        help_text=_("Nur relevant, wenn 'Datei hochladen...' ausgewählt ist"),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        last_edit_file = kwargs.pop('last_edit_file')
        super(PadForm, self).__init__(*args, **kwargs)

        choices = []
        if last_edit_file:
            choices.append(
                ('file', _("Quell-Datei des erstellten Protokolls (Stand: %(time)s)") %
                 {'time': defaultfilters.date(last_edit_file,
                                              "SHORT_DATETIME_FORMAT")})
            )
        choices.append(('upload', _("Datei hochladen...")))
        choices.append(('template', _("leere Vorlage")))
        self.fields['source'].choices = choices

    def clean(self):
        super(PadForm, self).clean()
        if self.cleaned_data.get('source') == 'upload':
            if not self.cleaned_data.get('template_file'):
                self.add_error(
                    "template_file", forms.ValidationError(
                        _("Es wurde keine Datei hochgeladen."))
                )
