from django.db import models


# Create your models here.
class UberModel(models.Model):
    email = models.EmailField(unique=True, blank=False, null=False)
    access_token = models.CharField(max_length=255, blank=False, null=False)
    name = models.CharField(max_length=50, blank=False, null=False)
