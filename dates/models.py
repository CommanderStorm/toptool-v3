from django.db import models

class Semester(models.Model):
    wintersemester = models.BooleanField()

    year = models.IntField()

    def __str__(self):
        if self.wintersemester:
            return "Wintersemester {0: 4}/{1: 2}".format(self.year,
                    self.year+1)
        else:
            return "Sommersemester {0: 4}".format(self.year)


class Ausschuss(models.Model):
    date = models.DateTimeField()

    room = models.CharField(
        max_length = 200,
    )

    semester = models.ForeignKey(
        Semester,
    )

    def __str__(self):
        return "Fachschaftsausschuss am {0} in {1}".format(self.date,
                self.room)


