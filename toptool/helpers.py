from django.contrib.auth.models import User  # pylint: disable=imported-auth-user
from django.core.handlers.wsgi import WSGIRequest


class AuthWSGIRequest(WSGIRequest):
    user: User
