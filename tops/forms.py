from ckeditor.widgets import CKEditorWidget
from django import forms
from django.db.models import Max

from meetings.models import Meeting
from .models import StandardTop, Top


class BaseTopForm(forms.ModelForm):
    authenticated: bool = True

    class Meta:
        model = Top
        exclude = ["meeting", "topid", "user"]
        widgets = {
            "description": CKEditorWidget(),
        }

    def __init__(self, *args, **kwargs):
        if "instance" in kwargs:
            self.meeting: Meeting = kwargs["instance"].meeting
        else:
            self.meeting = kwargs.pop("meeting")
        super().__init__(*args, **kwargs)
        if self.meeting.meetingtype.anonymous_tops:
            self.fields["author"].required = False
            self.fields["email"].required = False
        if not (self.meeting.meetingtype.attachment_tops and self.authenticated):
            del self.fields["attachment"]

    def save(self, commit=True):
        instance = super().save(False)

        instance.meeting = self.meeting
        instance.description = instance.description.replace("\r\n", "\n")
        instance.protokoll_templ = instance.protokoll_templ.replace("\r\n", "\n", )
        return instance


class AddTopForm(BaseTopForm):
    class Meta(BaseTopForm.Meta):
        exclude = BaseTopForm.Meta.exclude + ["protokoll_templ"]

    def __init__(self, *args, **kwargs):
        self.authenticated = kwargs.pop("authenticated")
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(False)

        # set_topid
        max_topid = self.meeting.top_set.filter(topid__lt=10000).aggregate(Max("topid"))["topid__max"]
        if max_topid is None:
            instance.topid = 1
        else:
            instance.topid = max_topid + 1

        if commit:
            instance.save()
        return instance


class EditTopForm(BaseTopForm):
    def __init__(self, *args, **kwargs):
        user_edit = kwargs.pop("user_edit")
        super().__init__(*args, **kwargs)
        if not self.meeting.meetingtype.protokoll or user_edit:
            del self.fields["protokoll_templ"]

    def save(self, commit=True):
        instance = super().save(False)

        if commit:
            instance.save()

        return instance


class AddStdForm(forms.ModelForm):
    class Meta:
        model = StandardTop
        exclude = ["meetingtype", "topid"]
        widgets = {
            "description": CKEditorWidget(),
        }

    def __init__(self, *args, **kwargs):
        self.meetingtype = kwargs.pop("meetingtype")
        super().__init__(*args, **kwargs)
        if not self.meetingtype.protokoll:
            del self.fields["protokoll_templ"]

    def save(self, commit=True):
        instance = super().save(False)

        instance.meetingtype = self.meetingtype
        max_topid = self.meetingtype.standardtop_set.aggregate(
            Max("topid"),
        )["topid__max"]
        if max_topid is None:
            instance.topid = 1
        else:
            instance.topid = max_topid + 1
        instance.description = instance.description.replace("\r\n", "\n")
        instance.protokoll_templ = instance.protokoll_templ.replace(
            "\r\n",
            "\n",
        )

        if commit:
            instance.save()

        return instance


class EditStdForm(forms.ModelForm):
    class Meta:
        model = StandardTop
        exclude = ["meetingtype", "topid"]
        widgets = {
            "description": CKEditorWidget(),
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs["instance"]
        super().__init__(*args, **kwargs)
        if not instance.meetingtype.protokoll:
            del self.fields["protokoll_templ"]

    def save(self, commit=True):
        instance = super().save(False)

        instance.description = instance.description.replace("\r\n", "\n")
        instance.protokoll_templ = instance.protokoll_templ.replace(
            "\r\n",
            "\n",
        )

        if commit:
            instance.save()

        return instance
