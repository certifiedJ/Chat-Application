from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.conf import settings

@receiver(user_logged_in)
def on_user_logged_in(sender, user, request, **kwargs):
    user.is_online = True
    user.save()

@receiver(user_logged_out)
def on_user_logged_out(sender, user, request, **kwargs):
    if user:
        user.is_online = False
        user.save()