from django import forms


class UserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "{0} ({1})".format(obj.get_full_name(), obj.username)


class UserMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return "{0} ({1})".format(obj.get_full_name(), obj.username)
