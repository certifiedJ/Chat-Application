from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Message
from django.contrib.auth.models import User

@login_required
def chat_view(request, recipient_id):
    recipient = User.objects.get(id=recipient_id)
    if request.method == 'POST':
        content = request.POST.get('message')
        if content:
            Message.objects.create(
                sender=request.user,
                recipient=recipient,
                content=content
            )
    messages = Message.objects.filter(
        sender__in=[request.user, recipient],
        recipient__in=[request.user, recipient]
    ).order_by('timestamp')

    return render(request, 'chat/chat.html', {
        'recipient': recipient,
        'messages': messages
    })

@login_required
def chat_home(request):
    return render(request, 'chat/chat.html')

def registration_view(request):
    return render(request, 'registration/register.html')