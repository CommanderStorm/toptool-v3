from django import forms

from .models import Top

class AddForm(forms.ModelForm):
    class Meta:
        model = Top
        exclude = ['meeting', 'topid', 'protokoll_templ']

    def __init__(self, *args, **kwargs):
        self.meeting = kwargs.pop('meeting')

        super(AddForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(AddForm, self).save(False)

        instance.meeting = self.meeting

        tops = self.meeting.top_set.order_by('topid')
        if not tops:
            instance.topid = 1
        else:
            instance.topid = tops[len(tops) - 1].topid+1

        if commit:
            instance.save()

        return instance


class EditForm(forms.ModelForm):
    class Meta:
        model = Top
        exclude = ['meeting', 'topid']

