from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    nif = models.CharField(max_length=9, unique=True, verbose_name="NIF")
    
    email = models.EmailField(unique=True, blank=False)

    def __str__(self):
        return self.username