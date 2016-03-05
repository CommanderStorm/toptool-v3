from django import forms
from django.contrib.auth.models import User

from .models import Protokoll

class SitzungsleitungsForm(forms.ModelForm):
    sitzungsleitung = forms.ModelChoiceField(queryset=None)
    protokoll = forms.FileField(required=False)
    
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

    def save(self, commit=True):
        instance = super(ProtokollForm, self).save(False)

        instance.meeting = self.meeting
        instance.t2t = self.t2t

        if commit:
            instance.save()

        return instance


