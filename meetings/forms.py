from bootstrap3_datetime.widgets import DateTimePicker
from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from .models import Meeting


class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        exclude = ['meetingtype', 'attendees']
        widgets = {
            'time': DateTimePicker(options={
                "format": "DD.MM.YYYY HH:mm",
                "minuteStepping": 5}),
            'topdeadline': DateTimePicker(options={
                "format": "DD.MM.YYYY HH:mm",
                "minuteStepping": 5}),
            }

    def __init__(self, *args, **kwargs):
        self.meetingtype = kwargs.pop('meetingtype')

        super(MeetingForm, self).__init__(*args, **kwargs)

        users = User.objects.filter(
            Q(user_permissions=self.meetingtype.get_permission()) |
            Q(groups__permissions=self.meetingtype.get_permission()))
        self.fields['sitzungsleitung'].queryset = users
        self.fields['protokollant'].queryset = users
        self.fields['time'].input_formats = ['%d.%m.%Y %H:%M']
        self.fields['topdeadline'].input_formats = ['%d.%m.%Y %H:%M']

    def save(self, commit=True):
        instance = super(MeetingForm, self).save(False)

        instance.meetingtype = self.meetingtype

        if commit:
            instance.save()

        return instance


class MeetingSeriesForm(forms.Form):
    start = forms.DateTimeField(
        input_formats=['%d.%m.%Y %H:%M'],
        widget=DateTimePicker(options={"format": "DD.MM.YYYY HH:mm",
                                       "minuteStepping": 5}),
        label=_("Start"),
    )

    end = forms.DateTimeField(
        input_formats=['%d.%m.%Y %H:%M'],
        widget=DateTimePicker(options={"format": "DD.MM.YYYY HH:mm",
                                       "minuteStepping": 5}),
        label=_("Ende"),
    )

    cycle = forms.ChoiceField(
        (
            (1, 'täglich'),
            (2, 'alle 2 Tage'),
            (7, 'wöchentlich'),
            (14, 'alle 2 Wochen'),
            (21, 'alle 3 Wochen'),
            (28, 'alle 4 Wochen'),
        ),
        label=_("Häufigkeit"),
    )

    room = forms.CharField(
        label=_("Raum"),
        max_length=200,
        required=False,
    )
