from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    email = models.CharField(max_length=250, unique=True)

class ChatHistory(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    user_chat = models.TextField(null=True, blank=True)
    response_chat = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
