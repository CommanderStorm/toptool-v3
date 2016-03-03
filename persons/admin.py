from django.contrib import admin

from .models import Person, Function, Attendee

admin.site.register(Function)
admin.site.register(Person)
admin.site.register(Attendee)


