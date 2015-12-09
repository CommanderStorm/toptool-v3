from django.db import models
from dates.models import Ausschuss

class Top(models.Model):
    title = models.CharField(
        max_length=200,
    )

    author = models.CharField(
        max_length=50,
    )

    email = models.CharField(
        max_length=100,
    )

    text = models.TextField()

    ausschuss = models.ForeignKey(
        Ausschuss,
    )

    date = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return "{0} ({1}, {2})".format(self.title, self.author, self.email)


