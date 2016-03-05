from subprocess import Popen, PIPE
import os
import glob

from django.db import models
from django.template.loader import get_template
from django.core.files.base import ContentFile, File

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
    )

    begin = models.TimeField()
    
    end = models.TimeField()

    # currently unused
    version = models.DateTimeField(
        auto_now=True,
    )

    approved = models.BooleanField()

    t2t = models.FileField(
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
            if str(line, 'utf-8').startswith("%!"):
                raise RuntimeError("Illegal command")
        self.t2t.open('r')
        text = self.t2t.read()

        functions = self.meeting.meetingtype.function_set
        attendees_list = ""
        for f in functions.iterator():
            attendees_list += ": " + f.protokollname + ":\n"
            attendees = self.meeting.attendee_set.filter(functions=f)
            attendees_list += ", ".join(map(lambda m: m.get_name(),
                attendees.iterator())) + "\n"

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

        os.remove(self.filepath + '.aux', self.filepath + '.out',
                self.filepath + '.toc', self.filepath + '.log')


