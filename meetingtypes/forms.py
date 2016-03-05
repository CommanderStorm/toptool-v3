from django import forms
from django.contrib.auth.models import Group, User

from .models import MeetingType

class MTForm(forms.Form):
    name = forms.CharField(max_length=200)
    groups = forms.ModelMultipleChoiceField(Group.objects.all(),
        required=False)
    users = forms.ModelMultipleChoiceField(User.objects.all(), required=False)
    admin_groups = forms.ModelMultipleChoiceField(Group.objects.all(),
        required=False)
    admin_users = forms.ModelMultipleChoiceField(User.objects.all(),
        required=False)
    mailinglist = forms.CharField(max_length=50, required=False)
    approve = forms.BooleanField(required=False)
    attendance = forms.BooleanField(required=False)
    attendance_with_func = forms.BooleanField(required=False)
    public = forms.BooleanField(required=False)
    other_in_tops = forms.BooleanField(required=False)


class MTAddForm(MTForm):
    shortname = forms.CharField(max_length=20)


