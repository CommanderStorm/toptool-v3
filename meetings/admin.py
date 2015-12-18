from django.contrib import admin

from .models import MeetingType, Meeting

admin.site.register(MeetingType)
admin.site.register(Meeting)


