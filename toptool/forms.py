from django import forms


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
