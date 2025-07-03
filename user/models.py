from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

import uuid

class CustomManager(BaseUserManager):
    def create_user(self, username, email, role="user", password=None, **extra_fields):
        if not all([username, email]):
            return ValueError('This field cannot be blank!')
        email = self.normalize_email(email)
        user = self.model(username, email, role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, role="admin", password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        # Incase this settings intend to be overrided
        if not extra_fields.get("is_staff"):
            return ValueError("Superuser account must have is_staff=True")
        if not extra_fields.get("is_superuser"):
            return ValueError("Superuser account must have is_superuser=True")
        
        return self.create_user(username, email, role, password, **extra_fields)

class CustomUser(AbstractUser):
    username = models.CharField(null=False, blank=False, max_length=50, unique=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(null=False, blank=False, unique=True)
    role = models.CharField(max_length=5, default="user")
    email_verified = models.BooleanField(default=False)
    token_valid = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    first_name = None
    last_name = None

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def save(self, *args, **kwargs):
        if self.username:
            self.username = self.username.capitalize()
        if self.email:
            self.email = self.email.lower()
        if self.role:
            self.role = self.role.lower()
        super().save(*args, **kwargs)

