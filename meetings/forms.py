from django import forms
from django.contrib.auth.models import User
from django.db.models import Q

from .models import Meeting

class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        exclude = ['meetingtype', 'attendees']

    def __init__(self, *args, **kwargs):
        self.meetingtype = kwargs.pop('meetingtype')

        super(MeetingForm, self).__init__(*args, **kwargs)

        users = User.objects.filter(
            Q(user_permissions=self.meetingtype.get_permission()) |
            Q(groups__permissions=self.meetingtype.get_permission()))
        self.fields['sitzungsleitung'].queryset = users
        self.fields['protokollant'].queryset = users


    def save(self, commit=True):
        instance = super(MeetingForm, self).save(False)

        instance.meetingtype = self.meetingtype

        if commit:
            instance.save()

        return instance


class MeetingSeriesForm(forms.Form):
    start = forms.DateTimeField()

    end = forms.DateTimeField()

    cycle = forms.ChoiceField((
        (1, 'täglich'),
        (2, 'alle 2 Tage'),
        (7, 'wöchentlich'),
        (14, 'alle 2 Wochen'),
        (21, 'alle 3 Wochen'),
        (28, 'alle 4 Wochen'),
    ))

    room = forms.CharField(
        required=False,
    )


