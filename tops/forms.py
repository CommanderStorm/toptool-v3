from django import forms
from django.db.models import Max

from ckeditor.widgets import CKEditorWidget

from .models import Top, StandardTop


class AddForm(forms.ModelForm):
    class Meta:
        model = Top
        exclude = ['meeting', 'topid', 'protokoll_templ', 'user']
        widgets = {
            'description': CKEditorWidget(),
        }

    def __init__(self, *args, **kwargs):
        self.meeting = kwargs.pop('meeting')
        authenticated = kwargs.pop('authenticated')
        super(AddForm, self).__init__(*args, **kwargs)
        if self.meeting.meetingtype.anonymous_tops:
            self.fields['author'].required = False
            self.fields['email'].required = False
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
        exclude = ['meeting', 'topid', 'user']
        widgets = {
            'description': CKEditorWidget(),
        }

    def __init__(self, *args, **kwargs):
        user_edit = kwargs.pop('user_edit')
        self.meeting = kwargs["instance"].meeting
        super(EditForm, self).__init__(*args, **kwargs)
        if self.meeting.meetingtype.anonymous_tops:
            self.fields['author'].required = False
            self.fields['email'].required = False
        if not self.meeting.meetingtype.attachment_tops:
            del self.fields['attachment']
        if not self.meeting.meetingtype.protokoll or user_edit:
            del self.fields['protokoll_templ']

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
        if not self.meetingtype.protokoll:
            del self.fields['protokoll_templ']

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

    def __init__(self, *args, **kwargs):
        instance = kwargs['instance']
        super(EditStdForm, self).__init__(*args, **kwargs)
        if not instance.meetingtype.protokoll:
            del self.fields['protokoll_templ']

    def save(self, commit=True):
        instance = super(EditStdForm, self).save(False)

        instance.description = instance.description.replace("\r\n", "\n")
        instance.protokoll_templ = instance.protokoll_templ.replace("\r\n",
        "\n")

        if commit:
            instance.save()

        return instance
