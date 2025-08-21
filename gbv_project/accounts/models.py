# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserManager

class User(AbstractUser):
    ROLE_CHOICES = [
        ('survivor', 'Survivor'),
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('counselor', 'Counselor'),
        ('lawyer', 'Lawyer'),
    ]
    username = None
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='survivor')
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
