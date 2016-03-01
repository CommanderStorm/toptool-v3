from django import forms
from django.contrib.auth.models import Group, User

from .models import MeetingType
from meetings.models import Meeting

class MTAddForm(forms.Form):
    name = forms.CharField(max_length=200)
    shortname = forms.CharField(max_length=20)
    group = forms.ModelChoiceField(Group.objects.all())
    admin_group = forms.ModelChoiceField(Group.objects.all(), required=False)
    admin_users = forms.ModelMultipleChoiceField(User.objects.exclude(
            is_superuser=True),required=False)
    mailinglist = forms.CharField(max_length=50, required=False)
    approve = forms.BooleanField(required=False)
    attendance = forms.BooleanField(required=False)


class MeetingAddForm(forms.ModelForm):
    class Meta:
        model = Meeting
        exclude = ['meetingtype', 'attendees']

    def __init__(self, *args, **kwargs):
        self.meetingtype = kwargs.pop('meetingtype')

        super(MeetingAddForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(MeetingAddForm, self).save(False)

        instance.meetingtype = self.meetingtype

        if commit:
            instance.save()

        return instance

