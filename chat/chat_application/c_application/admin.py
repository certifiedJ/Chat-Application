from django.contrib import admin
from .models import Message, Feedback

# Register your models here.
admin.site.register(Message)
admin.site.register(Feedback)