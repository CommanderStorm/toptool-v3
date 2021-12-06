from django import forms
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import Profile


def get_choice(color, name):
    return (color, format_html(
        '<span style="background-color:var(--background-color); color: {};">{}</span> ' +
        '<span style="background-color:{}; color: white;">{}</span>',
        mark_safe(color),
        name,
        mark_safe(color),
        name,
        ))


class ProfileForm(forms.ModelForm):
    color = forms.ChoiceField(
        choices=[get_choice(color, name) for color, name in (
            ("#337ab7", _("Blau (Standard)")),
            ("#329d6a", _("Grün")),
            ("#cf89f5", _("Violett")),
            ("#f52be8", _("Pink")),
            ("#ef5951", _("Rot")),
            ("#fdb839", _("Orange")),
            ("#797979", _("Grau")),
            ("black", _("Schwarz")),
        )],
        label=_("Farbe"),
        required=False,
        widget=forms.RadioSelect(attrs={'onchange': 'this.form.submit();'}),
    )

    class Meta:
        model = Profile
        fields = ("color", )
