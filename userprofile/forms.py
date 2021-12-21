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
            '<span style="color: {color};">{name}</span> <span '
            'style="background-color:{color}; color: {contrast_hex};">{name}</span>',
            color=color,
            contrast_hex=Profile.get_contrasting_hex(color),
            name=name,
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
                ("#000000", _("Schwarz")),
            )
        ],
        label=_("Farbe"),
        required=False,
        widget=forms.widgets.RadioSelect(attrs={"onchange": "document.getElementById('profileeditform').submit()"}),
    )

    colormode = forms.ChoiceField(
        choices=Profile.CM_CHOICES,
        label=_("Farbschema"),
        required=False,
        widget=forms.widgets.RadioSelect(attrs={"onchange": "document.getElementById('profileeditform').submit()"}),
    )

    class Meta:
        model = Profile
        fields = ("color", "colormode")
