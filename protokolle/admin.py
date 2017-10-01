from django.contrib import admin

from .models import Protokoll, Attachment

admin.site.register(Protokoll)
admin.site.register(Attachment)
