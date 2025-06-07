from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.
class ChatRoom(models.Model):
    name = models.CharField(max_length=100, unique=True)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_rooms')
    
    def __str__(self):
        return self.name


class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='received_messages',
        on_delete=models.CASCADE,
        null=True,  # Allow null for group messages
        blank=True  # Allow blank for group messages
    )
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    # Add a reactions field as a JSON dictionary: {emoji: [user_ids]}
    reactions = models.JSONField(default=dict, blank=True)
    
    
class CustomUser(AbstractUser):
    is_online = models.BooleanField(default=False)
    contacts = models.ManyToManyField('self', symmetrical=False, related_name='contacted_by', blank=True)


class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    feeling = models.CharField(max_length=20)
    comment = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
