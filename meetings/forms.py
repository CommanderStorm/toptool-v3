from bootstrap_datepicker_plus.widgets import DateTimePickerInput
from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils.formats import get_format
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
            "time": DateTimePickerInput(format="%d.%m.%Y %H:%M"),
            "topdeadline": DateTimePickerInput(format="%d.%m.%Y %H:%M"),
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
            self.fields["minute_takers"].widget = forms.MultipleHiddenInput()
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
    """
    Set up the time input formats for the given field.
    @param field: a DateTimeField
    @return: a DateTimeField with the time formats set
    """
    locale_formats = get_format("DATETIME_INPUT_FORMATS", lang=get_language())
    field.input_formats = locale_formats
    field.widget.format = get_appropriate_format(locale_formats)


def get_appropriate_format(formats: list) -> str:
    """
    @param formats: list of datetime formats
    @return: Get the first appropriate format from the given list of formats.
    """
    filtered = [f for f in formats if is_appropriate_format(f)]
    return filtered[0]


def is_appropriate_format(date_format: str):
    """
     we filter matching formats:
     - we don't need seconds,
     - want hours (and minutes),
     - want the long year and
     - don't want to start with the year
    """
    return "%S" not in date_format and "%H" in date_format and "%Y" in date_format and not date_format.startswith("%Y")


class MeetingSeriesForm(forms.Form):
    locale_formats = get_format("DATETIME_INPUT_FORMATS", lang=get_language())
    locale_format = get_appropriate_format(locale_formats)
    start = forms.DateTimeField(
        input_formats=locale_formats,
        widget=DateTimePickerInput(format=locale_format),
        label=_("Start"),
    )

    end = forms.DateTimeField(
        input_formats=locale_formats,
        widget=DateTimePickerInput(format=locale_format),
        label=_("Ende"),
    )

    cycle = forms.ChoiceField(
        choices=(
            (1, _("täglich")),
            (2, _("alle 2 Tage")),
            (7, _("wöchentlich")),
            (14, _("alle 2 Wochen")),
            (21, _("alle 3 Wochen")),
            (28, _("alle 4 Wochen")),
        ),
        label=_("Häufigkeit"),
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
