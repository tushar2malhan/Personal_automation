
from django.db import models
from django.contrib.auth.models import User

class Queries(models.Model):
    name = models.CharField(max_length=100, default='')
    roll = models.IntegerField(default=1)
    city = models.CharField(max_length=100, default='')

    class Meta :
        verbose_name_plural = 'Students'
        ordering = ['id']   # give column wise ordering

    def __str__(self):
        return str(self.id)          # return ur column here 

