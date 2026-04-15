from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import random



class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O email é obrigatório')
        if not extra_fields.get('nif'):
            raise ValueError('O NIF é obrigatório')
        
        

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('nif'):
            raise ValueError('O NIF é obrigatório para superuser')

        return self.create_user(username, email, password, **extra_fields)


class CustomUser(AbstractUser):
    nif = models.CharField(max_length=9, unique=True)
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True, null=True)

    REQUIRED_FIELDS = ['email', 'nif']

    objects = CustomUserManager()  

    def __str__(self):
        return self.username
    
    def generate_verification_code(self):
        code = str(random.randint(100000, 999999))
        self.verification_code = code
        self.save()
        return code