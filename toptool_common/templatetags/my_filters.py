from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
import re

register = template.Library()


@register.filter
@stringfilter
def strip_empty_lines(value):
    nonempty_lines = [l for l in value.splitlines() if l.strip()]
    return "\n".join(nonempty_lines)
