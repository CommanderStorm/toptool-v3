import re

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def strip_empty_lines(value):
    """
    Strips empty lines from a string.
    """
    nonempty_lines = [line for line in value.splitlines() if line.strip()]
    return "\n".join(nonempty_lines)


@register.filter
@stringfilter
def strip_li(value):
    """
    Strips <li> tags from a string.
    """
    regex = re.compile(r"^\s*<li>(.*)</li>")
    lines = []
    for line in value.splitlines():
        lines.append(regex.sub(r"  - \1", line))
    return "\n".join(lines)
