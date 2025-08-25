from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models
import uuid, os

class CustomManager(BaseUserManager):
    # For regular users
    def create_user(self, email, valid, password=None, **extra_fields):
        if not email:
            raise ValidationError("Email is required")
        if not password:
            raise ValidationError("Password is required")
        email = self.normalize_email(email)
        user = self.model(email=email, valid=valid, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    # For superusers
    def create_superuser(self, email, valid, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email=email, valid=valid, password=password, **extra_fields)
    
class CustomUser(AbstractUser):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(unique=True, null=False, blank=False)
    valid = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    first_name = None
    last_name = None
    username = None
   
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomManager()

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.strip().lower()
        super().save(*args, **kwargs)

class Link(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="links")
    originalURL = models.URLField(null=False, blank=False)
    shortURL = models.URLField(null=False, blank=True, unique=True)
    code = models.CharField(max_length=int(os.environ.get("CODE_LENGTH")), unique=True, null=False, blank=True)
    title = models.CharField(max_length=100, null=False, blank=False)
    clickCount = models.IntegerField(default=0)
    description = models.TextField(null=True, blank=True)
    dateCreated = models.DateTimeField(auto_now_add=True)
    dateModified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-dateCreated']

    def save(self, *args, **kwargs):
        if self.title:
            self.title = self.title.strip().lower()
        if self.description:
            self.description = self.description.strip().lower()
        super().save(*args, **kwargs)
