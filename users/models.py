from django.db import models

class User(models.Model):
    name = models.CharField(max_length=64)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    nif = models.CharField(max_length=9, unique=True)
    phone = models.CharField(max_length=9, unique=True)

    def __str__(self):
        return self.name