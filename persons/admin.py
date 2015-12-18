from django.contrib import admin

from .models import Person, Function

admin.site.register(Function)
admin.site.register(Person)


