from django.db import models
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

class MeetingType(models.Model):
    ADMIN = "_admin"
    APP_NAME = "meetingtypes."

    name = models.CharField(
        max_length = 200,
    )

    shortname = models.CharField(
        max_length = 20,
        unique = True,
    )

    mailinglist = models.CharField(
        max_length = 50,
    )

    approve = models.BooleanField()

    attendance = models.BooleanField()
    
    attendance_with_func = models.BooleanField()
    
    public = models.BooleanField()
    
    other_in_tops = models.BooleanField()

    def __str__(self):
        return self.name

    def permission(self):
        return MeetingType.APP_NAME + self.shortname

    def admin_permission(self):
        return MeetingType.APP_NAME + self.shortname + MeetingType.ADMIN

    def get_permission(self):
        content_type = ContentType.objects.get_for_model(MeetingType)
        codename = self.shortname
        return Permission.objects.get(content_type=content_type,
            codename=codename)

    def get_admin_permission(self):
        content_type = ContentType.objects.get_for_model(MeetingType)
        codename = self.shortname + MeetingType.ADMIN
        return Permission.objects.get(content_type=content_type,
            codename=codename)

    @property
    def past_meetings(self):
        return self.meeting_set.filter(time__lt=timezone.now())

    @property
    def upcoming_meetings(self):
        return self.meeting_set.filter(time__gte=timezone.now())

    @property
    def last_meeting(self):
        return self.past_meetings.latest('time')

    @property
    def next_meeting(self):
        return self.upcoming_meetings.earliest('time')


