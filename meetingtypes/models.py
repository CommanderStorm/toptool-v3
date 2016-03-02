from django.db import models
from django.contrib.auth.models import Permission

class MeetingType(models.Model):
    name = models.CharField(
        max_length = 200,
    )

    shortname = models.CharField(
        max_length = 20,
        unique = True,
    )

    permission = models.CharField(
        max_length = 200,
    )

    admin_permission = models.CharField(
        max_length = 200,
    )

    mailinglist = models.CharField(
        max_length = 50,
    )

    approve = models.BooleanField()

    attendance = models.BooleanField()
    
    public = models.BooleanField()

    def __str__(self):
        return self.name

    def get_permission(self):
        app_label, codename = self.permission.split('.')
        return Permission.objects.get(content_type__app_label=app_label,
            codename=codename)

    def get_admin_permission(self):
        app_label, codename = self.admin_permission.split('.')
        return Permission.objects.get(content_type__app_label=app_label,
            codename=codename)


