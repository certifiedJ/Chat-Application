from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Message
# from django.contrib.auth.models import User
from .forms import CustomUserCreationForm
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login


User = get_user_model()  # <--- Use this everywhere

@login_required
def chat_view(request, recipient_id):
    try:
        recipient = User.objects.get(id=recipient_id)
    except User.DoesNotExist:
        if request.is_ajax():
            return JsonResponse({'error': 'User not found.'}, status=404)
        messages.error(request, "User not found.")
        return redirect('chat_home')

    if request.method == 'POST':
        content = request.POST.get('message', '')
        image = request.FILES.get('image')
        msg = Message.objects.create(
            sender=request.user,
            recipient=recipient,
            content=content,
            image=image if image else None
        )
        # Return JSON for AJAX
        return JsonResponse({
            'sender': msg.sender.username,
            'content': msg.content,
            'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'image_url': msg.image.url if msg.image else None,
        })
    
    messages_qs = Message.objects.filter(
        sender__in=[request.user, recipient],
        recipient__in=[request.user, recipient]
    ).order_by('timestamp')
    
    messages_qs.filter(recipient=request.user, read=False).update(read=True)

    return render(request, 'chat/chat.html', {
        'recipient': recipient,
        'recipient_id': recipient_id,
        'messages': messages_qs,
        'request_user': request.user,
        'csrf_token': getattr(request, 'csrf_token', None),
    })
        
        

def chat_home(request):
    if not request.user.is_authenticated:
        messages.error(request, "Please log in to access chat.")
        return redirect('login')
    
    users = User.objects.exclude(id=request.user.id)
    # Calculate unread message counts for each user
    unread_counts = {
        user.id: Message.objects.filter(sender=user, recipient=request.user, read=False).count()
        for user in users
    }
    return render(request, 'chat/chat_home.html', {
        'users': users,
        'unread_counts': unread_counts,
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
    recipient_id = request.GET.get('recipient_id')
    if recipient_id and request.user.is_authenticated:
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
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'image_url': message.image.url if message.image else None,
        }
        for message in messages_qs
    ]
    return JsonResponse({'messages': message_data})

def logout_view(request):
    logout(request)
    return redirect('home')

def home(request):
    return render(request, 'chat/home.html')


def login_view(request):
    if request.method =="POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('chat_home')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'registration/login.html')