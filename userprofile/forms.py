from django import forms
from django.utils.functional import keep_lazy_text
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Profile


@keep_lazy_text
def get_color_choice(color, name):
    return (
        color,
        format_html(
            '<span style="background-color:white; color: {color};">{name}</span> <span '
            'style="background-color:{color}; color: white;">{name}</span>',
            color=color,
            name=name,
        ),
    )


@keep_lazy_text
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
                ("#329d6a", _("Grasgrün")),
                ("#cf89f5", _("Helllila")),
                ("#a79dc8", _("Lavendel")),
                ("#cf6679", _("Fuchsia")),
                ("#f52be8", _("Magenta")),
                ("#ef5951", _("Feueropal")),
                ("#fdb839", _("Gelb-orange")),
                ("#797979", _("Sonic Silver")),
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
