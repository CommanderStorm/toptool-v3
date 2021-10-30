# -*- coding: utf-8 -*-
import glob
import os
from subprocess import PIPE, Popen

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
from toptool.shortcuts import validate_file_type


def silentremove(path):
    try:
        os.remove(path)
    except OSError:
        pass


class IllegalCommandException(Exception):
    pass


class AttachmentStorage(FileSystemStorage):
    def url(self, name):
        attachment = Attachment.objects.get(attachment=name)
        return reverse(
            "showattachment_protokoll",
            args=[
                attachment.meeting.meetingtype.id,
                attachment.meeting.id,
                attachment.id,
            ],
        )


def protokoll_path(instance, filename):
    fileending = filename.rpartition(".")[2]
    # dir:      MEDIA_ROOT/protokolle/<meetingtype.id>/
    # filename: protokoll_<year>_<month>_<day>.<ending>
    return "protokolle/{0}/protokoll_{1:04}_{2:02}_{3:02}.{4}".format(
        instance.meeting.meetingtype.id,
        instance.meeting.time.year,
        instance.meeting.time.month,
        instance.meeting.time.day,
        filename.rpartition(".")[2],
    )


def attachment_path(instance, filename):
    # dir:      MEDIA_ROOT/attachments/<meetingtype.id>/
    # filename: protokoll_<year>_<month>_<day>_<topid>_<filname>
    return "attachments/{0}/protokoll_{1:04}_{2:02}_{3:02}_{4:02}_{5}".format(
        instance.meeting.meetingtype.id,
        instance.meeting.time.year,
        instance.meeting.time.month,
        instance.meeting.time.day,
        instance.meeting.attachment_set.count(),
        filename,
    )


class Attachment(models.Model):
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        verbose_name=_("Sitzung"),
    )

    name = models.CharField(
        _("Name"),
        max_length=100,
    )

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

    sort_order = models.IntegerField(
        _("Index für Sortierung"),
    )


class Protokoll(models.Model):
    meeting = models.OneToOneField(
        Meeting,
        primary_key=True,
        on_delete=models.CASCADE,
        verbose_name=_("Sitzung"),
    )

    begin = models.TimeField(
        _("Beginn der Sitzung"),
    )

    end = models.TimeField(
        _("Ende der Sitzung"),
    )

    approved = models.BooleanField(
        _("genehmigt"),
    )

    published = models.BooleanField(
        _("veröffentlicht"),
    )

    t2t = models.FileField(
        _("Protokoll"),
        upload_to=protokoll_path,
    )

    @property
    def fileurl(self):
        return self.t2t.url.rpartition(".")[0]

    @property
    def filepath(self):
        return self.t2t.path.rpartition(".")[0]

    @property
    def filename(self):
        return os.path.basename(self.t2t.path).rpartition(".")[0]

    def deleteFiles(self):
        filelist = glob.glob(self.filepath + ".*")
        for f in filelist:
            os.remove(f)

    def generate(self, request):
        self.t2t.open("r")
        lines = []
        for line in self.t2t:
            if (line.decode("utf-8") if type(line) == bytes else line).startswith("%!"):
                raise IllegalCommandException
            if not line.startswith("%"):
                lines.append(line)
        text = "\n".join(lines)
        TEMPLATETAGS_LINE = "{% load protokoll_tags %}\n"
        if self.meeting.meetingtype.attachment_protokoll:
            text = text.replace("[[ anhang", "{% anhang")
        if self.meeting.meetingtype.motion_tag:
            text = (
                text.replace(
                    "[[ antrag",
                    "{% antrag",
                )
                .replace(
                    "[[ endantrag",
                    "{% endantrag",
                )
                .replace(
                    "[[ motion",
                    "{% motion",
                )
                .replace(
                    "[[ endmotion",
                    "{% endmotion",
                )
            )
        if self.meeting.meetingtype.point_of_order_tag:
            text = (
                text.replace(
                    "[[ goantrag",
                    "{% goantrag",
                )
                .replace(
                    "[[ endgoantrag",
                    "{% endgoantrag",
                )
                .replace(
                    "[[ point_of_order",
                    "{% point_of_order",
                )
                .replace(
                    "[[ endpoint_of_order",
                    "{% endpoint_of_order",
                )
            )
        text = text.replace("]]", "%}")
        text_template = Template(TEMPLATETAGS_LINE + text)

        context = {
            "sitzungsleitung": self.meeting.sitzungsleitung.get_full_name,
            "minute_takers": self.meeting.min_takers_string(),
            "meeting": self.meeting,
            "request": request,
        }
        rendered_text = text_template.render(Context(context))

        attendees_list = None
        if self.meeting.meetingtype.attendance:
            attendees_list = ": " + "Alle Anwesenden" + ":\n"
            attendees = self.meeting.attendee_set.order_by("name")
            if attendees:
                attendees_list += (
                    ", ".join(
                        map(
                            lambda m: m.name,
                            attendees.iterator(),
                        ),
                    )
                    + "\n"
                )
            else:
                attendees_list += "//niemand anwesend//\n"

            if self.meeting.meetingtype.attendance_with_func:
                functions = self.meeting.meetingtype.function_set.order_by(
                    "sort_order",
                    "name",
                )
                for f in functions.iterator():
                    attendees_list += ": " + f.protokollname + ":\n"
                    attendees = self.meeting.attendee_set.filter(
                        functions=f,
                    ).order_by("name")
                    if attendees:
                        attendees_list += (
                            ", ".join(
                                map(
                                    lambda m: m.name,
                                    attendees.iterator(),
                                ),
                            )
                            + "\n"
                        )
                    else:
                        attendees_list += "//niemand anwesend//\n"

        context = {
            "meeting": self.meeting,
            "approved": ("Vorläufiges " if not self.approved else ""),
            "attendees_list": attendees_list,
            "text": rendered_text,
        }
        template_name = (
            self.meeting.meetingtype.custom_template or "protokolle/script.t2t"
        )

        script_template = get_template(template_name)
        script = script_template.render(context)

        for t in ["html", "tex", "txt"]:
            process = Popen(
                [
                    "txt2tags",
                    "-t",
                    t,
                    "-q",  # quiet
                    "-i",
                    "-",
                    "-o",
                    self.filepath + "." + t,
                ],
                stdin=PIPE,
                stdout=PIPE,
                stderr=PIPE,
            )
            (stdout, stderr) = process.communicate(
                input=script.encode("utf-8"),
            )
            if stderr:
                raise RuntimeError(stderr)

        # pdf
        path = self.filepath.rpartition("/")[0]
        cmd = [
            "pdflatex",
            "-interaction",
            "nonstopmode",
            "-output-directory",
            path,
            self.filepath + ".tex",
        ]

        process = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        if stderr:
            raise RuntimeError(stderr)

        process = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        if stderr:
            raise RuntimeError(stderr)

        silentremove(self.filepath + ".aux")
        silentremove(self.filepath + ".out")
        silentremove(self.filepath + ".toc")
        silentremove(self.filepath + ".log")

    def get_mail(self, request):
        # build url
        html_url = request.build_absolute_uri(
            reverse(
                "protokoll",
                args=[
                    self.meeting.meetingtype.id,
                    self.meeting.id,
                    "html",
                ],
            ),
        )
        pdf_url = request.build_absolute_uri(
            reverse(
                "protokoll",
                args=[
                    self.meeting.meetingtype.id,
                    self.meeting.id,
                    "pdf",
                ],
            ),
        )

        # protokoll as text
        with open(self.filepath + ".txt", "r") as f:
            protokoll_text = f.read()

        # text from templates
        subject_template = get_template(
            "protokolle/protokoll_mail_subject.txt",
        )
        subject = subject_template.render({"meeting": self.meeting}).rstrip()

        text_template = get_template("protokolle/protokoll_mail.txt")
        text = text_template.render(
            {
                "meeting": self.meeting,
                "html_url": html_url,
                "pdf_url": pdf_url,
                "protokoll_text": protokoll_text,
                "minute_takers": self.meeting.min_takers_string(),
                "minute_takers_mail": self.meeting.min_takers_mail_string(),
                "minutes_sender": request.user.get_full_name(),
            },
        )

        from_email = '"{0}" <{1}>'.format(
            request.user.get_full_name(),
            request.user.email,
        )

        to_email = '"{0}" <{1}>'.format(
            self.meeting.meetingtype.name,
            self.meeting.meetingtype.mailinglist,
        )

        return subject, text, from_email, to_email


# delete files when protokoll object is deleted
@receiver(pre_delete, sender=Protokoll)
def delete_protokoll(sender, **kwargs):
    instance = kwargs.get("instance")
    instance.deleteFiles()
