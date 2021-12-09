from django.contrib import admin

from .models import Attendee, Function, Person

admin.site.register(Function)
admin.site.register(Person)
admin.site.register(Attendee)
