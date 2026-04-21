from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import random
from django.conf import settings



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
    email_verified = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    receive_newsletter = models.BooleanField(default=False)

    REQUIRED_FIELDS = ['email', 'nif']

    objects = CustomUserManager()  

    def __str__(self):
        return self.username
    
    def generate_verification_code(self):
        code = str(random.randint(100000, 999999))
        self.verification_code = code
        self.save()
        return code

User = settings.AUTH_USER_MODEL

class UserPoints(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    def add_points(self, amount):
        self.points += amount
        self.save()

    def subtract_points(self, amount):
        if self.points >= amount:
            self.points -= amount
            self.save()
            return True
        return False

    def __str__(self):
        return f"{self.user} - {self.points} pontos"    
