# pylint: disable=unused-wildcard-import
# pylint: disable=wildcard-import
from toptool.settings.base_settings import *  # noqa: 401,F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "memory:",
    },
}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

MEDIA_ROOT = BASE_DIR / "test_media"  # noqa: F405
