from pathlib import Path
from wsgiref.util import FileWrapper

import magic
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models.fields.files import FieldFile
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _


def validate_file_type(upload: FieldFile) -> None:
    """
    Checks, if the file is in fact of a valid filetype and has the right extension

    @param upload: The file, the user has just uploaded
    """

    allowed_upload = _("Es können nur folgende Dateitypen hochgeladen werden: %(filetypes)s") % {
        "filetypes": ", ".join(settings.ALLOWED_FILE_TYPES.keys()),
    }
    filetype = magic.from_buffer(upload.file.read(1024), mime=True)
    if filetype not in settings.ALLOWED_FILE_TYPES.values():
        raise ValidationError(_("Der Dateityp wird nicht unterstützt. ") + allowed_upload)
    extension = Path(upload.name).suffix[1:].lower()
    if extension not in settings.ALLOWED_FILE_TYPES.keys():
        raise ValidationError(
            _("Diese Dateierweiterung %(extension)s wird nicht unterstützt. ")
            % {
                "extension": extension,
            }
            + allowed_upload,
        )


def prep_file(path: str) -> HttpResponse:
    with open(path, "rb") as file:
        filetype = magic.from_buffer(file.read(1024), mime=True)
    with open(path, "rb") as file:
        wrapper = FileWrapper(file)
    return HttpResponse(wrapper, content_type=filetype)
