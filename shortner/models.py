from django.db import models
from user.models import CustomUser
from django.utils.crypto import get_random_string
from dotenv import load_dotenv
import uuid, os

load_dotenv(override=True)

class LinkShortner(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="urls")
    long_url = models.URLField(null=False, blank=False, max_length=500)
    short_url = models.URLField(null=False, blank=False) 
    code = models.CharField(max_length=int(os.environ.get("CODE_LENGTH")), null=False, blank=False)
    title = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

