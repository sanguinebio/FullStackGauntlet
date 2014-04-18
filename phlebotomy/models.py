from django.db import models

class JsonDump(models.Model):
  json = models.TextField()
  time = models.DateTimeField()
