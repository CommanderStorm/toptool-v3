from django.db import models

class Function(models.Model):
    name = models.CharField(
        max_length = 200,
    )

    def __str__(self):
        return self.name

class Person(models.Model):
    name = models.CharField(
        max_length = 200,
    )

    functions = models.ManyToManyField(
        Function,
        blank = True,
    )

    def __str__(self):
        return "{0} ({1})".format(self.name, ', '.join(str(f) for
            f in self.functions.all()))


