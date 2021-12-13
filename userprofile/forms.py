from django import forms
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import Profile


def get_color_choice(color, name):
    return (
        color,
        format_html(
            '<span style="background-color:white; color: {};">{}</span> '
            + '<span style="background-color:{}; color: white;">{}</span>',
            mark_safe(color),  # nosec: predefined
            name,
            mark_safe(color),  # nosec: predefined
            name,
        ),
    )


def get_colormode_choice(colormode, name):
    return (
        colormode,
        format_html(
            "<span>{}</span>",
            name,
        ),
    )


class ProfileForm(forms.ModelForm):
    color = forms.ChoiceField(
        choices=[
            get_color_choice(color, name)
            for color, name in (
                ("#337ab7", _("Stahlblau (Standard)")),
                ("#329d6a", _("Meergrün")),
                ("#cf89f5", _("Violett")),
                ("#a79dc8", _("Lavendel")),
                ("#cf6679", _("Fuchsia")),
                ("#f52be8", _("Magenta")),
                ("#ef5951", _("Tomatenrot")),
                ("#fdb839", _("Goldenrod gelb")),
                ("#797979", _("Grau")),
                ("black", _("Schwarz")),
            )
        ],
        label=_("Farbe"),
        required=False,
        widget=forms.RadioSelect(attrs={"onchange": "this.form.submit();"}),
    )

    colormode = forms.ChoiceField(
        choices=[
            get_colormode_choice(color, name)
            for color, name in (
                (Profile.CM_DEFAULT, _("Systemstandard (Standard)")),
                (Profile.CM_LIGHT, _("Hell")),
                (Profile.CM_DARK, _("Dunkel")),
            )
        ],
        label=_("Farbschema"),
        required=False,
        widget=forms.RadioSelect(attrs={"onchange": "this.form.submit();"}),
    )

    class Meta:
        model = Profile
        fields = ("color", "colormode")
