from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

from toptool.forms import UserChoiceField, UserDualListField

from .models import Meeting


class MinuteTakersForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ("minute_takers",)

    minute_takers = UserDualListField(
        queryset=None,
        label="",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        self.meetingtype = kwargs.pop("meetingtype")

        super().__init__(*args, **kwargs)

        users = (
            get_user_model()
            .objects.filter(
                Q(user_permissions=self.meetingtype.get_permission())
                | Q(groups__permissions=self.meetingtype.get_permission()),
            )
            .distinct()
            .order_by("first_name", "last_name", "username")
        )
        self.fields["minute_takers"].queryset = users


class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        exclude = [
            "meetingtype",
            "attendees",
            "stdtops_created",
            "imported",
            "pad",
        ]
        widgets = {
            "time": forms.DateTimeInput(
                attrs={
                    "class": "my-datetimepicker",
                },
            ),
            "topdeadline": forms.DateTimeInput(
                attrs={
                    "class": "my-datetimepicker",
                },
            ),
        }

    sitzungsleitung = UserChoiceField(
        queryset=None,
        label=_("Sitzungsleitung"),
        required=False,
    )

    minute_takers = UserDualListField(
        queryset=None,
        label=_("Protokollant*innen"),
        required=False,
    )

    def clean(self):
        super().clean()
        time = self.cleaned_data.get("time")
        topdeadline = self.cleaned_data.get("topdeadline")

        if time and topdeadline and time < topdeadline:
            self.add_error(
                "topdeadline",
                forms.ValidationError(
                    _(
                        "Die TOP-Deadline kann nicht nach dem Beginn der Sitzung liegen.",
                    ),
                ),
            )

    def __init__(self, *args, **kwargs):
        self.meetingtype = kwargs.pop("meetingtype")

        super().__init__(*args, **kwargs)

        users = (
            get_user_model()
            .objects.filter(
                Q(user_permissions=self.meetingtype.get_permission())
                | Q(groups__permissions=self.meetingtype.get_permission()),
            )
            .distinct()
            .order_by("first_name", "last_name", "username")
        )
        self.fields["sitzungsleitung"].queryset = users
        self.fields["minute_takers"].queryset = users
        # setup input formats
        setup_time_formats(self.fields["time"])
        setup_time_formats(self.fields["topdeadline"])
        # conditionally hide some fields
        if not self.meetingtype.protokoll:
            self.fields["minute_takers"].widget = forms.HiddenInput()
        if not self.meetingtype.tops or not self.meetingtype.top_deadline:
            self.fields["topdeadline"].widget = forms.HiddenInput()

    def save(self, commit=True):
        instance = super().save(False)

        instance.meetingtype = self.meetingtype

        if commit:
            instance.save()

        if self.meetingtype.protokoll:
            self.save_m2m()

        return instance


def setup_time_formats(field):
    field.input_formats = ["%d.%m.%Y %H:%M", "%m/%d/%Y %I:%M %p"]
    field.widget.format = (
        "%m/%d/%Y %I:%M %p" if get_language() == "en" else "%d.%m.%Y %H:%M"
    )


class MeetingSeriesForm(forms.Form):
    start = forms.DateTimeField(
        input_formats=[
            "%d.%m.%Y %H:%M",
            "%m/%d/%Y %I:%M %p",
        ],
        widget=forms.DateTimeInput(
            attrs={
                "class": "my-datetimepicker",
            },
        ),
        label=_("Start"),
    )

    end = forms.DateTimeField(
        input_formats=[
            "%d.%m.%Y %H:%M",
            "%m/%d/%Y %I:%M %p",
        ],
        widget=forms.DateTimeInput(
            attrs={
                "class": "my-datetimepicker",
            },
        ),
        label=_("Ende"),
    )

    cycle = forms.ChoiceField(
        choices=(
            (1, _("taeglich")),
            (2, _("alle 2 Tage")),
            (7, _("woechentlich")),
            (14, _("alle 2 Wochen")),
            (21, _("alle 3 Wochen")),
            (28, _("alle 4 Wochen")),
        ),
        label=_("Haeufigkeit"),
    )

    top_deadline = forms.ChoiceField(
        choices=(
            ("no", _("Keine Deadline")),
            ("day", _("1 Tag vor der Sitzung")),
            ("hour", _("1 Stunde vor der Sitzung")),
        ),
        help_text=_(
            "Frist, bis zu der TOPs eingereicht werden können. "
            "Wenn keine Frist gesetzt ist, können bis zum Beginn der Sitzung "
            "TOPs eingetragen werden.",
        ),
        label=_("TOP-Deadline"),
        required=False,
    )

    room = forms.CharField(
        label=_("Raum"),
        max_length=200,
        required=False,
    )

    def clean(self):
        super().clean()
        start = self.cleaned_data.get("start")
        end = self.cleaned_data.get("end")

        if start and end and end < start:
            validation_error = forms.ValidationError(
                _("Das End-Datum kann nicht vor dem Start-Datum liegen."),
            )
            self.add_error("end", validation_error)

    def __init__(self, *args, **kwargs):
        self.meetingtype = kwargs.pop("meetingtype")
        super().__init__(*args, **kwargs)
        setup_time_formats(self.fields["start"])
        setup_time_formats(self.fields["end"])
        if not self.meetingtype.tops or not self.meetingtype.top_deadline:
            self.fields["top_deadline"].widget = forms.HiddenInput()
