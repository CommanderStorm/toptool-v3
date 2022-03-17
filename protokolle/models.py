import datetime
import glob
import os
from contextlib import suppress
from subprocess import PIPE, Popen  # nosec: used in a secure manner
from typing import Any, Optional

from django.conf import settings
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import Context, Template, TemplateSyntaxError
from django.template.loader import get_template
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

# pylint: disable-next=unused-import
import meetings.models
from toptool.utils.files import validate_file_type
from toptool.utils.typing import AuthWSGIRequest


class IllegalCommandException(Exception):
    pass


class AttachmentStorage(FileSystemStorage):
    def url(self, name):
        attachment = Attachment.objects.get(attachment=name)
        return reverse("protokolle:show_attachment_protokoll", args=[attachment.id])


def protokoll_path(instance: "Protokoll", filename: str) -> str:
    # dir:      MEDIA_ROOT/protokolle/<meetingtype.id>/
    # filename: protokoll_<year>_<month>_<day>.<ending>
    file_ending = filename.rpartition(".")[2]
    time: datetime.datetime = instance.meeting.time
    new_filename = f"protokoll_{time.year:04}_{time.month:02}_{time.day:02}.{file_ending}"
    return os.path.join("protokolle", instance.meeting.meetingtype.id, new_filename)


def attachment_path(instance: "Attachment", filename: str) -> str:
    # dir:      MEDIA_ROOT/attachments/<meetingtype.id>/
    # filename: protokoll_<year>_<month>_<day>_<topid>_<filname>
    meeting: "meetings.models.Meeting" = instance.meeting
    time: datetime.datetime = meeting.time
    attachment_count = meeting.attachment_set.count()
    new_filename = f"protokoll_{time.year:04}_{time.month:02}_{time.day:02}_{attachment_count:02}_{filename}"
    return os.path.join("attachments", meeting.meetingtype.id, new_filename)


class Attachment(models.Model):
    meeting = models.ForeignKey("meetings.Meeting", on_delete=models.CASCADE, verbose_name=_("Sitzung"))
    name = models.CharField(_("Name"), max_length=100)
    attachment = models.FileField(
        _("Anhang"),
        upload_to=attachment_path,
        validators=[validate_file_type],
        storage=AttachmentStorage(),
        help_text=_("Erlaubte Dateiformate: %(filetypes)s").format(
            {"filetypes": ", ".join(settings.ALLOWED_FILE_TYPES.keys())},
        ),
    )

    sort_order = models.IntegerField(_("Index für Sortierung"))

    @property
    def full_filename(self) -> str:
        raw_filename: str = os.path.basename(self.attachment.path)
        return raw_filename

    def __str__(self):
        return f"{self.name} ({self.full_filename})"


class Protokoll(models.Model):
    meeting = models.OneToOneField(
        "meetings.Meeting",
        primary_key=True,
        on_delete=models.CASCADE,
        verbose_name=_("Sitzung"),
    )

    begin = models.TimeField(_("Beginn der Sitzung"))
    end = models.TimeField(_("Ende der Sitzung"))

    approved = models.BooleanField(_("genehmigt"))
    published = models.BooleanField(_("veröffentlicht"))

    t2t = models.FileField(_("Protokoll"), upload_to=protokoll_path)

    @property
    def fileurl(self) -> str:
        """
        @return: the url the file is located at
        """
        url: str = self.t2t.url
        return url.rpartition(".")[0]

    @property
    def filepath(self) -> str:
        """
        @return: the path the file is located at including the filename, but without the extension
        """
        return os.path.join(self.base_filepath, self.filename)

    @property
    def base_filepath(self) -> str:
        """
        @return: the path the file is located at including the filename, but without the extension
        """
        path: str = self.t2t.path
        return os.path.dirname(path)

    @property
    def full_filename(self) -> str:
        """
        @return: filename of the file including the extension
        """
        full_filename: str = os.path.basename(self.t2t.path)
        return full_filename

    @property
    def filename(self) -> str:
        """
        @return: filename of the file excluding the extension
        """
        return self.full_filename.rpartition(".")[0]

    def delete_files(self) -> None:
        """
        Deletes all associated files
        """
        files = glob.glob(self.filepath + ".*")
        for file in files:
            os.remove(file)

    def handle_generation(self, request: AuthWSGIRequest) -> Optional[HttpResponse]:
        """
        Handles all the different error-cases, that can occur during the protocol generation pipeline.

        @param request: a WSGIRequest by a logged-in user
        @return: a HttpResponse if the Protokoll generation was successful
        """

        try:
            script: str = self._render_protokoll_to_t2t_script(request)
            self._generate_different_file_formats(script)
        except TemplateSyntaxError as err:
            error = _("Template-Syntaxfehler: {error_message}").format(error_message=err.args[0])
            messages.error(request, error)
        except IllegalCommandException:
            error_message = _("Befehle (Zeilen, die mit '%!' beginnen) sind nicht erlaubt")
            error = _("Template-Syntaxfehler: {error_message}").format(error_message=error_message)
            messages.error(request, error)
        except UnicodeDecodeError:
            error = _("Encoding-Fehler: Die Protokoll-Datei ist nicht UTF-8 kodiert.")
            messages.error(request, error)
        except RuntimeError as err:
            lines = err.args[0].decode("utf-8").strip().splitlines()
            if lines[-1].startswith("txt2tags.error"):
                messages.error(request, lines[-1])
            else:
                # delete protokoll, which failed to generate
                self.delete()
                raise err
        else:
            # the Protocol is done 🥳
            return redirect("protokolle:success_protokoll", self.meeting.id)
        # delete protokoll, which failed to generate
        self.delete()
        return None

    def _generate_different_file_formats(self, script: str) -> None:
        """
        Generates the pdf, html and txt file from a protokoll
        """
        # generate html, txt and tex files
        for target in ["html", "txt", "tex"]:
            args = [
                "txt2tags",
                "-t",
                target,
                "-q",  # quiet
                "-i",
                "-",
                "-o",
                self.filepath + "." + target,
            ]
            with Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE) as process:  # nosec: used in a secure manner.
                _stdout, stderr = process.communicate(input=script.encode("utf-8"))
            if stderr:
                raise RuntimeError(stderr)
        # generate pdf files from tex files
        cmd = [
            "pdflatex",
            "-interaction",
            "nonstopmode",
            "-output-directory",
            self.base_filepath,
            self.filepath + ".tex",
        ]
        for _i in range(2):
            with Popen(cmd, stdout=PIPE, stderr=PIPE) as process:  # nosec: used in a secure manner
                _stdout, stderr = process.communicate()
            if stderr:
                raise RuntimeError(stderr)
        # remove tex files
        for extension in [".aux", ".out", ".toc", ".log"]:
            with suppress(OSError):
                os.remove(self.filepath + extension)

    def _render_protokoll_to_t2t_script(self, request: AuthWSGIRequest) -> str:
        text = self._get_text_from_t2t()
        text_template: Template = self._convert_text_to_template(text)
        text_context = {
            "sitzungsleitung": self.meeting.sitzungsleitung_string,
            "minute_takers": self.meeting.min_takers_str_protokill,
            "meeting": self.meeting,
            "request": request,
        }
        rendered_text: str = text_template.render(Context(text_context))
        context = {
            "meeting": self.meeting,
            "approved": ("Vorläufiges " if not self.approved else ""),
            "attendees_list": self._generate_attendance_list(),
            "text": rendered_text,
        }
        template_name: str = self.meeting.meetingtype.custom_template or "protokolle/script.t2t"
        script_template: Template = get_template(template_name)
        script: str = script_template.render(context)
        return script

    def _generate_attendance_list(self) -> Optional[str]:
        if not self.meeting.meetingtype.attendance:
            return None
        attendees_list = ": Alle Anwesenden:\n"
        attendees = self.meeting.attendee_set.order_by("name")
        if attendees:
            attendees_list += ", ".join(atendee.name for atendee in attendees.iterator())
            attendees_list += "\n"
        else:
            attendees_list += "//niemand anwesend//\n"

        if self.meeting.meetingtype.attendance_with_func:
            functions = self.meeting.meetingtype.function_set.order_by(
                "sort_order",
                "name",
            )
            for function in functions.iterator():
                attendees_list += f": {function.protokollname}:\n"
                attendees_for_function = attendees.filter(functions=function)
                if attendees_for_function:
                    attendees_list += ", ".join(atendee.name for atendee in attendees_for_function.iterator())
                    attendees_list += "\n"
                else:
                    attendees_list += "//niemand anwesend//\n"
        return attendees_list

    def _convert_text_to_template(self, text: str) -> Template:
        if self.meeting.meetingtype.attachment_protokoll:
            text = text.replace("[[ anhang", "{% anhang")
        tags_with_end = []
        if self.meeting.meetingtype.motion_tag:
            tags_with_end = ["antrag", "motion"]
        if self.meeting.meetingtype.point_of_order_tag:
            tags_with_end += ["goantrag", "point_of_order"]
        for tag in tags_with_end:
            text = text.replace(f"[[ {tag}", f"{{% {tag}")
            text = text.replace(f"[[ end{tag}", f"{{% end{tag}")
        text = text.replace("]]", "%}")
        return Template("{% load protokoll_tags %}\n" + text)

    def _get_text_from_t2t(self) -> str:
        with open(self.t2t.path, "r", encoding="UTF-8") as file:
            lines: list[str] = []
            line: str
            for line in file.readline():
                if line.startswith("%!"):
                    raise IllegalCommandException
                if not line.startswith("%"):
                    lines.append(line)
            return "\n".join(lines)

    def get_mail(self, request: AuthWSGIRequest) -> tuple[str, str, str, str]:
        # build url
        html_url = request.build_absolute_uri(reverse("protokolle:show_protokoll", args=[self.meeting.id, "html"]))
        pdf_url = request.build_absolute_uri(reverse("protokolle:show_protokoll", args=[self.meeting.id, "pdf"]))

        # protokoll as text
        with open(self.filepath + ".txt", "r", encoding="UTF-8") as file:
            protokoll_text = file.read()

        # text from templates
        subject_template = get_template("protokolle/mail/protokoll_mail_subject.txt")
        subject = subject_template.render({"meeting": self.meeting}).rstrip()

        text_template = get_template("protokolle/mail/protokoll_mail.txt")
        text_context = {
            "meeting": self.meeting,
            "html_url": html_url,
            "pdf_url": pdf_url,
            "protokoll_text": protokoll_text,
            "minute_takers": self.meeting.min_takers_str_protokill,
            "minute_takers_mail": self.meeting.min_takers_mail_joined,
            "minutes_sender": request.user.get_full_name(),
        }
        text = text_template.render(text_context)

        from_email = f'"{request.user.get_full_name()}" <{request.user.email}>'
        to_email = f'"{self.meeting.meetingtype.name}" <{self.meeting.meetingtype.mailinglist}>'

        return subject, text, from_email, to_email

    def __str__(self):
        return f"Protokoll for {self.meeting} ({self.begin}-{self.end})"


# pylint: disable=unused-argument
@receiver(pre_delete, sender=Protokoll)
def delete_protokoll(sender: type[Protokoll], instance: Protokoll, **kwargs: Any) -> None:
    """
    Signal listener that deletes all asociated files when a protokoll object is deleted.

    @param sender: the sender of the event
    @param instance: the Protokoll
    """
    instance.delete_files()


# pylint: enable=unused-argument
