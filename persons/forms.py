from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Attendee, Person, Function


class SelectPersonForm(forms.Form):
    person_label = forms.CharField(
            label=_("Person"),
            widget=forms.TextInput(attrs={'size': 80}))
    person = forms.CharField(widget=forms.HiddenInput(), required=False)


class EditAttendeeForm(forms.ModelForm):
    class Meta:
        model = Attendee
        fields = ['functions']


class AddPersonForm(forms.ModelForm):
    class Meta:
        model = Person
        exclude = ['meetingtype', 'version']

    def __init__(self, *args, **kwargs):
        self.meetingtype = kwargs.pop('meetingtype')

        super(AddPersonForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(AddPersonForm, self).save(False)

        instance.meetingtype = self.meetingtype

        if commit:
            instance.save()

        return instance


class AddFunctionForm(forms.ModelForm):
    class Meta:
        model = Function
        exclude = ['meetingtype']

    def __init__(self, *args, **kwargs):
        self.meetingtype = kwargs.pop('meetingtype')

        super(AddFunctionForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(AddFunctionForm, self).save(False)

        instance.meetingtype = self.meetingtype

        if commit:
            instance.save()

        return instance
