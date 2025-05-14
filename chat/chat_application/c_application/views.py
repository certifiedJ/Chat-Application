from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Message
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm
from django.http import JsonResponse
from .models import Message
from django.shortcuts import redirect
from django.contrib.auth import logout

@login_required
def chat_view(request, recipient_id):
    try:
        recipient = User.objects.get(id=recipient_id)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('chat_home')

    if request.method == 'POST':
        content = request.POST.get('message')
        if content:
            Message.objects.create(
                sender=request.user,
                recipient=recipient,
                content=content
            )

    messages_qs = Message.objects.filter(
        sender__in=[request.user, recipient],
        recipient__in=[request.user, recipient]
    ).order_by('timestamp')

    return render(request, 'chat/chat.html', {
        'recipient': recipient,
        'messages': messages_qs,
        'request_user': request.user,
        'csrf_token': getattr(request, 'csrf_token', None),
    })


def chat_home(request):
    if not request.user.is_authenticated:
        messages.error(request, "Please log in to access chat.")
        return redirect('login')
    
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'chat/chat_home.html', {
        'users': users,
        'request_user': request.user,
        'csrf_token': getattr(request, 'csrf_token', None),
    })

def registration_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully!')
            return redirect('login')
        else:
            form = CustomUserCreationForm()
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def fetch_messages(request):
    # Optionally filter messages for chat between the current user and recipient
    # If recipient_id is passed as GET param, filter for those two users
    recipient_id = request.GET.get('recipient_id')
    if recipient_id and request.user.is_authenticated:
        from django.contrib.auth.models import User
        try:
            recipient = User.objects.get(id=recipient_id)
            messages_qs = Message.objects.filter(
                sender__in=[request.user, recipient],
                recipient__in=[request.user, recipient]
            ).order_by('timestamp')
        except User.DoesNotExist:
            return JsonResponse({'messages': []})
    else:
        messages_qs = Message.objects.all().order_by('timestamp')
    message_data = [
        {
            'sender': message.sender.username,
            'content': message.content,
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
        for message in messages_qs
    ]
    return JsonResponse({'messages': message_data})



def logout_view(request):
    logout(request)
    return redirect('home')


def home(request):
    return render(request, 'chat/home.html')