from django.db import models


class Ads(models.Model):
	name = models.CharField(max_length=100)
	author = models.CharField(max_length=100)
	price = models.IntegerField(blank=True, null=True)
	description = models.CharField(max_length=1000)
	address = models.CharField(max_length=100)
	is_published = models.BooleanField(default=False)


class Categories(models.Model):
	name = models.CharField(max_length=100)

