from django.contrib import admin

from .models import MeetingTypePreference, Profile

admin.site.register(Profile)
admin.site.register(MeetingTypePreference)
