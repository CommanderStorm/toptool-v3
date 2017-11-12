# -*- coding: utf-8 -*-
from subprocess import Popen, PIPE
import os
import glob

from django.db import models
from django.template import Template, Context
from django.template.loader import get_template
from django.core.urlresolvers import reverse
from django.core.files.base import ContentFile, File
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.core.files.storage import FileSystemStorage

from meetings.models import Meeting
from toptool.shortcuts import validate_file_type


class AttachmentStorage(FileSystemStorage):
    def url(self, name):
        attachment = Attachment.objects.get(attachment=name)
        return reverse('showattachment_protokoll',
                args=[attachment.meeting.meetingtype.id,
                attachment.meeting.id, attachment.id])


def protokoll_path(instance, filename):
    fileending = filename.rpartition(".")[2]
    # dir:      MEDIA_ROOT/protokolle/<meetingtype.id>/
    # filename: protokoll_<year>_<month>_<day>.<ending>
    return 'protokolle/{0}/protokoll_{1:04}_{2:02}_{3:02}.{4}'.format(
        instance.meeting.meetingtype.id,
        instance.meeting.time.year,
        instance.meeting.time.month,
        instance.meeting.time.day,
        filename.rpartition(".")[2],
    )


def attachment_path(instance, filename):
    # dir:      MEDIA_ROOT/attachments/<meetingtype.id>/
    # filename: protokoll_<year>_<month>_<day>_<topid>_<filname>
    return 'attachments/{0}/protokoll_{1:04}_{2:02}_{3:02}_{4:02}_{5}'.format(
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
        verbose_name=_("Meeting"),
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
        self.t2t.open('r')
        lines = []
        for line in self.t2t:
            if (line.decode('utf-8') if type(line) == bytes else line).\
                    startswith("%!"):
                raise RuntimeError("Illegal command")
            if not line.startswith("%"):
                lines.append(line)
        text = "\n".join(lines)
        TEMPLATETAGS_LINE = "{% load protokoll_tags %}\n"
        text = text.replace(
            "[[ anhang", "{% anhang").replace(
            "[[ antrag", "{% antrag").replace(
            "[[ endantrag", "{% endantrag").replace(
            "[[ goantrag", "{% goantrag").replace(
            "[[ endgoantrag", "{% endgoantrag").replace(
            "]]", "%}")
        text_template = Template(TEMPLATETAGS_LINE + text)
        context = {
            'sitzungsleitung': self.meeting.sitzungsleitung.get_full_name,
            'protokollant': self.meeting.protokollant.get_full_name,
            'meeting': self.meeting,
            'request': request,
        }
        rendered_text = text_template.render(Context(context))

        attendees_list = None
        if self.meeting.meetingtype.attendance:
            attendees_list = ": " + "Alle Anwesenden" + ":\n"
            attendees = self.meeting.attendee_set.order_by("name")
            if attendees:
                attendees_list += ", ".join(map(lambda m: m.name,
                                                attendees.iterator())) + "\n"
            else:
                attendees_list += "//niemand anwesend//\n"

            if self.meeting.meetingtype.attendance_with_func:
                functions = self.meeting.meetingtype.function_set.order_by(
                    'sort_order', 'name')
                for f in functions.iterator():
                    attendees_list += ": " + f.protokollname + ":\n"
                    attendees = self.meeting.attendee_set.filter(
                        functions=f).order_by("name")
                    if attendees:
                        attendees_list += ", ".join(map(lambda m: m.name,
                                                attendees.iterator())) + "\n"
                    else:
                        attendees_list += "//niemand anwesend//\n"

        context = {
            'meeting': self.meeting,
            'approved': ("Vorläufiges " if not self.approved else ""),
            'attendees_list': attendees_list,
            'text': rendered_text,
        }
        script_template = get_template('protokolle/script.t2t')
        script = script_template.render(context)

        for t in ['html', 'tex', 'txt']:
            process = Popen([
                'txt2tags',
                '-t', t,
                '-q',           # quiet
                '-i', '-',
                '-o', self.filepath + "." + t,
                ], stdin=PIPE, stdout=PIPE, stderr=PIPE)
            (stdout, stderr) = process.communicate(
                input=script.encode('utf-8'))
            if stderr:
                raise RuntimeError(stderr)

        # pdf
        path = self.filepath.rpartition("/")[0]
        cmd = [
            'pdflatex',
            '-interaction', 'nonstopmode',
            '-output-directory', path,
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

        os.remove(self.filepath + '.aux')
        os.remove(self.filepath + '.out')
        os.remove(self.filepath + '.toc')
        os.remove(self.filepath + '.log')

    def get_mail(self, request):
        # build url
        html_url = request.build_absolute_uri(
            reverse('protokoll', args=[self.meeting.meetingtype.id,
                self.meeting.id, "html"]))
        pdf_url = request.build_absolute_uri(
            reverse('protokoll', args=[self.meeting.meetingtype.id,
                self.meeting.id, "pdf"]))

        # protokoll as text
        with open(self.filepath + ".txt", "r") as f:
            protokoll_text = f.read()

        # text from templates
        subject_template = get_template(
            'protokolle/protokoll_mail_subject.txt')
        subject = subject_template.render({'meeting': self.meeting}).rstrip()

        text_template = get_template('protokolle/protokoll_mail.txt')
        text = text_template.render({
            'meeting': self.meeting,
            'html_url': html_url,
            'pdf_url': pdf_url,
            'protokoll_text': protokoll_text,
            'protokollant': self.meeting.protokollant,
        })

        from_email = '"{0}" <{1}>'.format(
            self.meeting.protokollant.get_full_name(),
            self.meeting.protokollant.email,
        )

        to_email = '"{0}" <{1}>'.format(
            self.meeting.meetingtype.name,
            self.meeting.meetingtype.mailinglist,
        )

        return (subject, text, from_email, to_email)


# delete files when protokoll object is deleted
@receiver(pre_delete, sender=Protokoll)
def delete_protokoll(sender, **kwargs):
    instance = kwargs.get('instance')
    instance.deleteFiles()
