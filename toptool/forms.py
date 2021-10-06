from django import forms
from django.utils.translation import gettext_lazy as _


class DualListField(forms.ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        super(DualListField, self).__init__(*args, **kwargs)
        self.widget = forms.SelectMultiple(attrs={'class': 'duallistbox'})


class UserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "{0} ({1})".format(obj.get_full_name(), obj.username)


class UserDualListField(DualListField):
    def label_from_instance(self, obj):
        return "{0} ({1})".format(obj.get_full_name(), obj.username)


class EmailForm(forms.Form):
    subject = forms.CharField(
        label=_("Betreff"),
    )

    text = forms.CharField(
        widget=forms.Textarea,
        label=_("Text"),
    )
