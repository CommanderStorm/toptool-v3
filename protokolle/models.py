# -*- coding: utf-8 -*-
import glob
import os
from contextlib import suppress
from subprocess import PIPE, Popen  # nosec: used in a secure manner
from typing import List, Optional

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.template import Context, Template
from django.template.loader import get_template
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from meetings.models import Meeting
from toptool.utils.files import validate_file_type


def silent_remove(path):
    with suppress(OSError):
        os.remove(path)


class IllegalCommandException(Exception):
    pass


class AttachmentStorage(FileSystemStorage):
    def url(self, name):
        attachment = Attachment.objects.get(attachment=name)
        return reverse("protokolle:show_attachment_protokoll", args=[attachment.meeting.id, attachment.id])


def protokoll_path(instance, filename):
    file_ending = filename.rpartition(".")[2]
    # dir:      MEDIA_ROOT/protokolle/<meetingtype.id>/
    # filename: protokoll_<year>_<month>_<day>.<ending>
    return (
        f"protokolle/{instance.meeting.meetingtype.id}/"
        f"protokoll_{instance.meeting.time.year:04}_{instance.meeting.time.month:02}_"
        f"{instance.meeting.time.day:02}.{file_ending}"
    )


def attachment_path(instance, filename):
    # dir:      MEDIA_ROOT/attachments/<meetingtype.id>/
    # filename: protokoll_<year>_<month>_<day>_<topid>_<filname>
    return (
        f"attachments/{instance.meeting.meetingtype.id}/"
        f"protokoll_{instance.meeting.time.year:04}_{instance.meeting.time.month:02}_"
        f"{instance.meeting.time.day:02}_{instance.meeting.attachment_set.count():02}_{filename}"
    )


class Attachment(models.Model):
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        verbose_name=_("Sitzung"),
    )
    name = models.CharField(_("Name"), max_length=100)
    attachment = models.FileField(
        _("Anhang"),
        upload_to=attachment_path,
        validators=[validate_file_type],
        storage=AttachmentStorage(),
        help_text=_("Erlaubte Dateiformate: %(filetypes)s")
        % {
            "filetypes": ", ".join(settings.ALLOWED_FILE_TYPES.keys()),
        },
    )

    sort_order = models.IntegerField(_("Index für Sortierung"))

    @property
    def full_filename(self):
        return os.path.basename(self.attachment.path)

    def __str__(self):
        return f"{self.name} ({self.full_filename})"


class Protokoll(models.Model):
    meeting = models.OneToOneField(
        Meeting,
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
    def fileurl(self):
        return self.t2t.url.rpartition(".")[0]

    @property
    def filepath(self):
        return self.t2t.path.rpartition(".")[0]

    @property
    def full_filename(self):
        return os.path.basename(self.t2t.path)

    @property
    def filename(self):
        return self.full_filename.rpartition(".")[0]

    def delete_files(self):
        files = glob.glob(self.filepath + ".*")
        for file in files:
            os.remove(file)

    def generate(self, request):
        text = self._get_text_from_t2t()
        text_template = self._convert_text_to_template(text)
        text_context = {
            "sitzungsleitung": self.meeting.sitzungsleitung.get_full_name,
            "minute_takers": self.meeting.min_takers_joined(),
            "meeting": self.meeting,
            "request": request,
        }
        rendered_text = text_template.render(Context(text_context))

        context = {
            "meeting": self.meeting,
            "approved": ("Vorläufiges " if not self.approved else ""),
            "attendees_list": self._generate_attendance_list(),
            "text": rendered_text,
        }
        template_name = self.meeting.meetingtype.custom_template or "protokolle/script.t2t"

        script_template = get_template(template_name)
        script = script_template.render(context)

        for target in ["html", "tex", "txt"]:
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
        self._generate_pdf()

    def _generate_pdf(self):
        path = self.filepath.rpartition("/")[0]
        cmd = [
            "pdflatex",
            "-interaction",
            "nonstopmode",
            "-output-directory",
            path,
            self.filepath + ".tex",
        ]
        for _i in range(2):
            with Popen(cmd, stdout=PIPE, stderr=PIPE) as process:  # nosec: used in a secure manner
                _stdout, stderr = process.communicate()
            if stderr:
                raise RuntimeError(stderr)
        for extension in [".aux", ".out", ".toc", ".log"]:
            silent_remove(self.filepath + extension)

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

    def _convert_text_to_template(self, text):
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

    def _get_text_from_t2t(self):
        with open(self.t2t.path, "r") as file:
            lines: List[str] = []
            for line in file.readline():
                save_line: str = line.decode("utf-8") if isinstance(line, bytes) else line
                if save_line.startswith("%!"):
                    raise IllegalCommandException
                if not save_line.startswith("%"):
                    lines.append(save_line)
            return "\n".join(lines)

    def get_mail(self, request):
        # build url
        html_url = request.build_absolute_uri(reverse("protokolle:show_protokoll", args=[self.meeting.id, "html"]))
        pdf_url = request.build_absolute_uri(reverse("protokolle:show_protokoll", args=[self.meeting.id, "pdf"]))

        # protokoll as text
        with open(self.filepath + ".txt", "r") as file:
            protokoll_text = file.read()

        # text from templates
        subject_template = get_template("protokolle/protokoll_mail_subject.txt")
        subject = subject_template.render({"meeting": self.meeting}).rstrip()

        text_template = get_template("protokolle/protokoll_mail.txt")
        text_context = {
            "meeting": self.meeting,
            "html_url": html_url,
            "pdf_url": pdf_url,
            "protokoll_text": protokoll_text,
            "minute_takers": self.meeting.min_takers_joined(),
            "minute_takers_mail": self.meeting.min_takers_mail_joined(),
            "minutes_sender": request.user.get_full_name(),
        }
        text = text_template.render(text_context)

        from_email = f'"{request.user.get_full_name()}" <{request.user.email}>'
        to_email = f'"{self.meeting.meetingtype.name}" <{self.meeting.meetingtype.mailinglist}>'

        return subject, text, from_email, to_email

    def __str__(self):
        return f"Protokoll for {self.meeting} ({self.begin}-{self.end})"


# pylint: disable=unused-argument
# delete files when protokoll object is deleted
@receiver(pre_delete, sender=Protokoll)
def delete_protokoll(sender, **kwargs):
    instance = kwargs.get("instance")
    instance.delete_files()


# pylint: enable=unused-argument
