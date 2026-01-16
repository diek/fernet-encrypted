from django.db import models


class Province(models.Model):
    name = models.CharField(max_length=32, unique=True)
    abbreviation = models.CharField(max_length=2, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class City(models.Model):
    HALIFAX_ID = 1

    name = models.CharField(max_length=32, unique=True)
    province = models.ForeignKey(Province, models.PROTECT)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "cities"

    def __str__(self):
        return "%s, %s" % (self.name, self.province.abbreviation)


class Relationship(models.Model):
    name = models.CharField(max_length=32, unique=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name
