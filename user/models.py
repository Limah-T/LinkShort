from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

import uuid

class CustomManager(BaseUserManager):
    def create_user(self, first_name, last_name, email, role="user", password=None, **extra_fields):
        if not all([first_name, last_name, email]):
            return ValueError('This field cannot be blank!')
        email = self.normalize_email(email)
        user = self.model(first_name, last_name, email, role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, email, role="admin", password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        # Incase this settings intend to be overrided
        if not extra_fields.get("is_staff"):
            return ValueError("Superuser account must have is_staff=True")
        if not extra_fields.get("is_superuser"):
            return ValueError("Superuser account must have is_superuser=True")
        
        return self.create_user(first_name, last_name, email, role, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(null=False, blank=False, max_length=50)
    last_name = models.CharField(null=False, blank=False, max_length=50)
    email = models.EmailField(null=False, blank=False, unique=True)
    role = models.CharField(max_length=5, default="user")
    email_verified = models.BooleanField(default=False)
    token_valid = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def save(self, *args, **kwargs):
        if self.first_name:
            self.first_name = self.first_name.capitalize()
        if self.last_name:
            self.last_name = self.last_name.capitalize()
        if self.email:
            self.email = self.email.lower()
        if self.role:
            self.role = self.role.lower()
        super().save(*args, **kwargs)

