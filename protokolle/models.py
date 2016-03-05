from subprocess import Popen, PIPE
import os
import glob

from django.db import models
from django.template.loader import get_template
from django.core.urlresolvers import reverse
from django.core.files.base import ContentFile, File
from django.core.mail import send_mail
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy  as _

from meetings.models import Meeting


def protokoll_path(instance, filename):
    fileending = filename.rpartition(".")[2]
    # dir:      MEDIA_ROOT/protokolle/<meetingtype.shortname>/
    # filename: protokoll_<year_<month>_<day>.<ending>
    return 'protokolle/{0}/protokoll_{1:04}_{2:02}_{3:02}.{4}'.format(
        instance.meeting.meetingtype.shortname,
        instance.meeting.time.year,
        instance.meeting.time.month,
        instance.meeting.time.day,
        filename.rpartition(".")[2],
    )

class Protokoll(models.Model):
    meeting = models.OneToOneField(
        Meeting,
        primary_key=True,
        on_delete = models.CASCADE,
        verbose_name = _("Sitzung"),
    )

    begin = models.TimeField(
        _("Beginn der Sitzung"),
    )
    
    end = models.TimeField(
        _("Ende der Sitzung"),
    )

    # currently unused
    version = models.DateTimeField(
        _("Version"),
        auto_now=True,
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

    def deleteFiles(self):
        filelist = glob.glob(self.filepath + ".*")
        for f in filelist:
            os.remove(f)


    def generate(self):
        self.t2t.open('r')
        for line in self.t2t:
            if (line.decode('utf-8') if type(line) == bytes else line
                    ).startswith("%!"):
                raise RuntimeError("Illegal command")
        self.t2t.open('r')
        text = self.t2t.read()

        functions = self.meeting.meetingtype.function_set
        attendees_list = ""
        for f in functions.iterator():
            attendees_list += ": " + f.protokollname + ":\n"
            attendees = self.meeting.attendee_set.filter(functions=f)
            if attendees:
                attendees_list += ", ".join(map(lambda m: m.get_name(),
                    attendees.iterator())) + "\n"
            else:
                attendees_list += "//niemand anwesend//\n"

        context = {
            'meeting': self.meeting,
            'approved': ("Vorläufiges " if not self.approved else ""),
            'attendees_list': attendees_list,
            'text': text,
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
            (stdout, stderr) = process.communicate(input=script.encode('utf-8'))
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

    def send_mail(self, request):
        # build url
        html_url = request.build_absolute_uri(reverse('protokoll',
            args=[self.meeting.id, "html"]))
        pdf_url = request.build_absolute_uri(reverse('protokoll',
            args=[self.meeting.id, "pdf"]))

        # protokoll as text
        with open(self.filepath + ".txt", "r") as f:
            protokoll_text = f.read()

        # text from templates
        subject_template = get_template('protokolle/protokoll_mail_subject.txt')
        subject = subject_template.render({ 'meeting': self.meeting }).rstrip()

        text_template = get_template('protokolle/protokoll_mail.txt')
        text = text_template.render({
            'meeting': self.meeting,
            'html_url': html_url,
            'pdf_url': pdf_url,
            'protokoll_text': protokoll_text,
            'protokollant': self.meeting.protokollant,
        })

        # send
        send_mail(subject, text, self.meeting.meetingtype.mailinglist,
            [self.meeting.meetingtype.mailinglist], fail_silently=False)


# delete files when protokoll object is deleted
@receiver(pre_delete, sender=Protokoll)
def delete_protokoll(sender, **kwargs):
    instance = kwargs.get('instance')
    instance.deleteFiles()


