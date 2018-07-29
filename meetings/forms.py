from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language

from toptool.forms import UserChoiceField

from .models import Meeting


class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        exclude = ['meetingtype', 'attendees', 'stdtops_created', 'imported',
            'pad']
        widgets = {
            'time': forms.DateTimeInput(attrs={
                'class': 'my-datetimepicker',
            }),
            'topdeadline': forms.DateTimeInput(attrs={
                'class': 'my-datetimepicker',
             }),
        }

    sitzungsleitung = UserChoiceField(
        queryset=None,
        label=_("Sitzungsleitung"),
        required=False,
    )

    protokollant = UserChoiceField(
        queryset=None,
        label=_("Protokollant*in"),
        required=False,
    )

    def clean(self):
        super(MeetingForm, self).clean()
        time = self.cleaned_data.get('time')
        topdeadline = self.cleaned_data.get('topdeadline')

        if time and topdeadline and time < topdeadline:
            self.add_error('topdeadline', forms.ValidationError(
                _("Die TOP-Deadline kann nicht nach dem Beginn der Sitzung liegen."),
            ))

    def __init__(self, *args, **kwargs):
        self.meetingtype = kwargs.pop('meetingtype')

        super(MeetingForm, self).__init__(*args, **kwargs)

        users = User.objects.filter(
            Q(user_permissions=self.meetingtype.get_permission()) |
            Q(groups__permissions=self.meetingtype.get_permission())
            ).distinct().order_by('first_name', 'last_name', 'username')
        self.fields['sitzungsleitung'].queryset = users
        self.fields['protokollant'].queryset = users
        self.fields['time'].input_formats = [
            '%d.%m.%Y %H:%M',
            '%m/%d/%Y %I:%M %p',
        ]
        self.fields['time'].widget.format = (
            '%m/%d/%Y %I:%M %p'
            if get_language() == 'en'
            else '%d.%m.%Y %H:%M'
        )
        self.fields['topdeadline'].input_formats = [
            '%d.%m.%Y %H:%M',
            '%m/%d/%Y %I:%M %p',
        ]
        self.fields['topdeadline'].widget.format = (
            '%m/%d/%Y %I:%M %p'
            if get_language() == 'en'
            else '%d.%m.%Y %H:%M'
        )
        if not self.meetingtype.protokoll:
            self.fields['protokollant'].widget = forms.HiddenInput()
        if not self.meetingtype.tops or not self.meetingtype.top_deadline:
            self.fields['topdeadline'].widget = forms.HiddenInput()


    def save(self, commit=True):
        instance = super(MeetingForm, self).save(False)

        instance.meetingtype = self.meetingtype

        if commit:
            instance.save()

        return instance


class MeetingSeriesForm(forms.Form):
    start = forms.DateTimeField(
        input_formats=[
            '%d.%m.%Y %H:%M',
            '%m/%d/%Y %I:%M %p',
        ],
        widget = forms.DateTimeInput(attrs={
            'class': 'my-datetimepicker',
        }),
        label=_("Start"),
    )

    end = forms.DateTimeField(
        input_formats=[
            '%d.%m.%Y %H:%M',
            '%m/%d/%Y %I:%M %p',
        ],
        widget = forms.DateTimeInput(attrs={
            'class': 'my-datetimepicker',
        }),
        label=_("Ende"),
    )

    cycle = forms.ChoiceField(
        choices=(
            (1, _('taeglich')),
            (2, _('alle 2 Tage')),
            (7, _('woechentlich')),
            (14, _('alle 2 Wochen')),
            (21, _('alle 3 Wochen')),
            (28, _('alle 4 Wochen')),
        ),
        label=_("Haeufigkeit"),
    )

    top_deadline = forms.ChoiceField(
        choices=(
            ('no', _('Keine Deadline')),
            ('day', _('1 Tag vor der Sitzung')),
            ('hour', _('1 Stunde vor der Sitzung')),
        ),
        help_text=_(
            "Frist, bis zu der TOPs eingereicht werden können. "
            "Wenn keine Frist gesetzt ist, können bis zum Beginn der Sitzung "
            "TOPs eingetragen werden."
        ),
        label=_("TOP-Deadline"),
        required=False,
    )

    room = forms.CharField(
        label=_("Raum"),
        max_length=200,
        required=False,
    )

    def clean(self):
        super(MeetingSeriesForm, self).clean()
        start = self.cleaned_data.get('start')
        end = self.cleaned_data.get('end')

        if start and end and end < start:
            self.add_error('end', forms.ValidationError(
                _("Das End-Datum kann nicht vor dem Start-Datum liegen."),
            ))

    def __init__(self, *args, **kwargs):
        self.meetingtype = kwargs.pop('meetingtype')
        super(MeetingSeriesForm, self).__init__(*args, **kwargs)
        self.fields['start'].widget.format = (
            '%m/%d/%Y %I:%M %p'
            if get_language() == 'en'
            else '%d.%m.%Y %H:%M'
        )
        self.fields['end'].widget.format = (
            '%m/%d/%Y %I:%M %p'
            if get_language() == 'en'
            else '%d.%m.%Y %H:%M'
        )
        if not self.meetingtype.tops or not self.meetingtype.top_deadline:
            self.fields['top_deadline'].widget = forms.HiddenInput()
