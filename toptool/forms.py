from typing import Any

from django import forms

# pylint: disable=imported-auth-user
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class DualListField(forms.ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = forms.SelectMultiple(attrs={"class": "duallistbox"})


class UserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj: Any) -> str:
        if isinstance(obj, User):
            return f"{obj.get_full_name()} ({obj.username})"
        return "invalid-user"


class UserDualListField(DualListField):
    def label_from_instance(self, obj: Any) -> str:
        if isinstance(obj, User):
            return f"{obj.get_full_name()} ({obj.username})"
        return "invalid-user"


class EmailForm(forms.Form):
    subject = forms.CharField(label=_("Betreff"))
    text = forms.CharField(
        widget=forms.Textarea,
        label=_("Text"),
    )
