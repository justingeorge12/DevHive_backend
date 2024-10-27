from django.db import models

# Create your models here.


class Tag(models.Model):
    name = models.CharField(max_length=40, unique=True)
    description = models.CharField(max_length=350)
    question_count = models.IntegerField(default=0)
    