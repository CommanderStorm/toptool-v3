from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def get_keycloak_status():
    """
    Returns if Keycloak is enabled or not.
    @return: settings.USE_KEYCLOAK
    """
    return settings.USE_KEYCLOAK
