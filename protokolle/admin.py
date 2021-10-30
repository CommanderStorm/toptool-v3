from django.contrib import admin

from .models import Attachment, Protokoll

admin.site.register(Protokoll)
admin.site.register(Attachment)
