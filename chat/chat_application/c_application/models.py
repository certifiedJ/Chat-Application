from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.
class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    
    
class CustomUser(AbstractUser):
    is_online = models.BooleanField(default=False)