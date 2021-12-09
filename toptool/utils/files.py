import magic
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_file_type(upload):
    filetype = magic.from_buffer(upload.file.read(1024), mime=True)
    if filetype not in settings.ALLOWED_FILE_TYPES.values():
        raise ValidationError(
            _(
                "Der Dateityp wird nicht unterstützt. Es können nur folgende "
                "Dateitypen hochgeladen werden: %(filetypes)s",
            )
            % {"filetypes": ", ".join(settings.ALLOWED_FILE_TYPES.keys())},
        )
