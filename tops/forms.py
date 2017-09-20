from django import forms
from django.db.models import Max

from ckeditor.widgets import CKEditorWidget

from .models import Top, StandardTop


class AddForm(forms.ModelForm):
    class Meta:
        model = Top
        exclude = ['meeting', 'topid', 'protokoll_templ']
        widgets = {
            'description': CKEditorWidget(),
        }

    def __init__(self, *args, **kwargs):
        self.meeting = kwargs.pop('meeting')
        authenticated = kwargs.pop('authenticated')
        super(AddForm, self).__init__(*args, **kwargs)
        if not self.meeting.meetingtype.attachment_tops or not authenticated:
            del self.fields['attachment']

    def save(self, commit=True):
        instance = super(AddForm, self).save(False)

        instance.meeting = self.meeting
        max_topid = self.meeting.top_set.filter(topid__lt=10000).aggregate(
                Max('topid'))['topid__max']
        if max_topid is None:
            instance.topid = 1
        else:
            instance.topid = max_topid + 1
        instance.description = instance.description.replace("\r\n", "\n")
        instance.protokoll_templ = instance.protokoll_templ.replace("\r\n",
            "\n")

        if commit:
            instance.save()

        return instance


class EditForm(forms.ModelForm):
    class Meta:
        model = Top
        exclude = ['meeting', 'topid']
        widgets = {
            'description': CKEditorWidget(),
        }

    def __init__(self, *args, **kwargs):
        self.meeting = kwargs["instance"].meeting
        super(EditForm, self).__init__(*args, **kwargs)
        if not self.meeting.meetingtype.attachment_tops:
            del self.fields['attachment']

    def save(self, commit=True):
        instance = super(EditForm, self).save(False)

        instance.description = instance.description.replace("\r\n", "\n")
        instance.protokoll_templ = instance.protokoll_templ.replace("\r\n",
            "\n")

        if commit:
            instance.save()

        return instance


class AddStdForm(forms.ModelForm):
    class Meta:
        model = StandardTop
        exclude = ['meetingtype', 'topid']
        widgets = {
            'description': CKEditorWidget(),
        }

    def __init__(self, *args, **kwargs):
        self.meetingtype = kwargs.pop('meetingtype')

        super(AddStdForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(AddStdForm, self).save(False)

        instance.meetingtype = self.meetingtype
        max_topid = self.meetingtype.standardtop_set.aggregate(
                Max('topid'))['topid__max']
        if max_topid is None:
            instance.topid = 1
        else:
            instance.topid = max_topid + 1
        instance.description = instance.description.replace("\r\n", "\n")
        instance.protokoll_templ = instance.protokoll_templ.replace("\r\n",
        "\n")

        if commit:
            instance.save()

        return instance


class EditStdForm(forms.ModelForm):
    class Meta:
        model = StandardTop
        exclude = ['meetingtype', 'topid']
        widgets = {
            'description': CKEditorWidget(),
        }

    def save(self, commit=True):
        instance = super(EditStdForm, self).save(False)

        instance.description = instance.description.replace("\r\n", "\n")
        instance.protokoll_templ = instance.protokoll_templ.replace("\r\n",
        "\n")

        if commit:
            instance.save()

        return instance
