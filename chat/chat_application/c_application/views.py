from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import ChatRoom, Message, Feedback
from django.contrib import messages
from .models import Message
# from django.contrib.auth.models import User
from .forms import CustomUserCreationForm
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_POST

from django.conf import settings
from django.http import JsonResponse
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant
import os

from django.core.mail import send_mail
from django.conf import settings


#
User = get_user_model() 

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
    users = request.user.contacts.all()  # Ensure `contacts` field exists in the CustomUser model
    rooms = ChatRoom.objects.filter(participants=request.user)
    unread_counts = {
        user.id: Message.objects.filter(sender=user, recipient=request.user, read=False).count()
        for user in users
    }
    # Add unread counts for group rooms (messages in room, not sent by current user, and not read by current user)
    room_unread_counts = {
        room.id: Message.objects.filter(
            room=room,
            recipient__isnull=True,  # group messages
            read=False
        ).exclude(sender=request.user).count()
        for room in rooms
    }

    # Handle room creation from chat_home
    if request.method == "POST" and 'room_name' in request.POST:
        room_name = request.POST['room_name']
        if not ChatRoom.objects.filter(name=room_name).exists():
            room = ChatRoom.objects.create(name=room_name)
            room.participants.add(request.user)
            return redirect('room_detail', room_id=room.id)
        else:
            messages.error(request, "A room with this name already exists. Please choose a different name.")

    return render(request, 'chat/chat_home.html', {
        'users': users,
        'rooms': rooms,
        'unread_counts': unread_counts,
        'room_unread_counts': room_unread_counts,
        'request_user': request.user,
    })

def registration_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            inviter_id = request.GET.get('invited_by')
            if inviter_id:
                try:
                    inviter = User.objects.get(id=inviter_id)
                    inviter.contacts.add(user)
                    user.contacts.add(inviter)
                except User.DoesNotExist:
                    pass
            messages.success(request, 'Account created successfully!')
            return redirect('login')
        else:
            form = CustomUserCreationForm()
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def fetch_messages(request):
    room_id = request.GET.get('room_id')
    recipient_id = request.GET.get('recipient_id')
    if room_id and request.user.is_authenticated:
        try:
            room = ChatRoom.objects.get(id=room_id)
            messages_qs = Message.objects.filter(room=room).order_by('timestamp')
        except ChatRoom.DoesNotExist:
            return JsonResponse({'messages': []})
    elif recipient_id and request.user.is_authenticated:
        try:
            recipient = User.objects.get(id=recipient_id)
            messages_qs = Message.objects.filter(
                sender__in=[request.user, recipient],
                recipient__in=[request.user, recipient]
            ).order_by('timestamp')
        except User.DoesNotExist:
            return JsonResponse({'messages': []})
    else:
        messages_qs = Message.objects.none()
    message_data = [
        {
            'sender': message.sender.username,
            'content': message.content,
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'image_url': message.image.url if message.image else None,
            'id': message.id,
            'reactions': message.reactions,
        }
        for message in messages_qs
    ]
    # Push notification support
    if request.GET.get("check_unread") and request.user.is_authenticated:
        # Check for any unread direct or group messages for this user
        unread_direct = Message.objects.filter(recipient=request.user, read=False).exists()
        unread_group = Message.objects.filter(
            recipient__isnull=True, read=False
        ).exclude(sender=request.user).exists()
        # Check for any new reactions to your messages
        reacted = False
        # Only check for reactions on messages not sent by you
        my_messages = Message.objects.filter(recipient=request.user) | Message.objects.filter(room__participants=request.user)
        for msg in my_messages:
            if msg.reactions:
                for emoji, users in msg.reactions.items():
                    # If someone else (not you) reacted
                    if any(str(uid) != str(request.user.id) for uid in users):
                        reacted = True
                        break
            if reacted:
                break
        notify = None
        if unread_direct:
            notify = "You have a new direct message."
        elif unread_group:
            notify = "You have a new group message."
        elif reacted:
            notify = "Someone reacted to your message."
        return JsonResponse({'notify': notify})
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


# Typing Indicator Views (add near the bottom of the file)
@csrf_exempt
@login_required
def set_typing(request, recipient_id):
    if request.method == 'POST':
        cache.set(f'typing_{request.user.id}_{recipient_id}', True, timeout=2)
        return JsonResponse({'status': 'ok'})

@login_required
def is_typing(request, recipient_id):
    key = f'typing_{recipient_id}_{request.user.id}'
    is_typing_flag = cache.get(key, False)
    return JsonResponse({'is_typing': is_typing_flag})


@login_required
def room_list(request):
    rooms = ChatRoom.objects.all()
    if request.method == "POST":
        room_name = request.POST.get("room_name")
        if room_name and not ChatRoom.objects.filter(name=room_name).exists():
            room = ChatRoom.objects.create(name=room_name)
            room.participants.add(request.user)
            return redirect('room_detail', room_id=room.id)
        elif room_name:
            messages.error(request, "A room with this name already exists. Please choose a different name.")
    return render(request, 'chat/room_list.html', {'rooms': rooms})

@login_required
def room_detail(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    messages = Message.objects.filter(room=room).order_by('timestamp')
    # Mark all unread group messages as read for this user (if not sent by self)
    Message.objects.filter(room=room, recipient__isnull=True, read=False).exclude(sender=request.user).update(read=True)
    if request.method == "POST":
        content = request.POST.get("message")
        image = request.FILES.get("image")
        if content or image:
            Message.objects.create(
                sender=request.user,
                room=room,
                content=content or '',
                image=image,
                recipient=None  # Explicitly set recipient to None for group messages
            )
            return redirect('room_detail', room_id=room.id)
    return render(request, 'chat/chat.html', {'room': room, 'messages': messages})


def delete_room(request, room_id):
    if request.method == "POST":
        room = get_object_or_404(ChatRoom, id=room_id)
        room.delete()
    return redirect('chat_home')

@csrf_exempt
def submit_feedback(request):
    if request.method == "POST":
        feeling = request.POST.get("feeling")
        comment = request.POST.get("comment", "")
        user = request.user if request.user.is_authenticated else None
        Feedback.objects.create(user=user, feeling=feeling, comment=comment)
        return JsonResponse({"ok": True})
    return JsonResponse({"ok": False}, status=400)

@csrf_exempt
@require_POST
@login_required
def react_to_message(request):
    import json
    message_id = request.POST.get("message_id")
    emoji = request.POST.get("emoji")
    user_id = str(request.user.id)
    try:
        msg = Message.objects.get(id=message_id)
        reactions = msg.reactions or {}
        if emoji not in reactions:
            reactions[emoji] = []
        if user_id in reactions[emoji]:
            # Remove reaction if user already reacted
            reactions[emoji].remove(user_id)
            # Clean up empty emoji lists
            if not reactions[emoji]:
                del reactions[emoji]
        else:
            # Add reaction if not already present
            reactions[emoji].append(user_id)
        msg.reactions = reactions
        msg.save()
        return JsonResponse({"ok": True, "reactions": reactions})
    except Message.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Message not found"}, status=404)
    


@login_required
def video_token(request):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    api_key_sid = os.getenv("TWILIO_API_KEY_SID")
    api_key_secret = os.getenv("TWILIO_API_KEY_SECRET")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")

    identity = request.user.username
    room = request.GET.get('room', 'default-room')

    token = AccessToken(account_sid, api_key_sid, api_key_secret, identity=identity)
    video_grant = VideoGrant(room=room)
    token.add_grant(video_grant)
    return JsonResponse({'token': token.to_jwt()})



# New invite_user view (supports both email and SMS via Twilio)
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

@require_POST
@login_required
def invite_user(request):
    email = request.POST.get('email')
    #phone = request.POST.get('phone')
    invite_link = request.build_absolute_uri(f'/register/?invited_by={request.user.id}')

    if email:
        subject = "🎉 Invitation to MyChatApp!"
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [email]
        context = {
            'inviter': request.user.username,
            'invite_link': invite_link,
        }

        text_content = f"{request.user.username} invited you to join MyChatApp! Register here: {invite_link}"
        html_content = render_to_string('chat/invite_user.html', context)  

        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=True)

        return JsonResponse({'success': True, 'message': 'Invitation email sent.'})

    #elif phone:
        # Send SMS using Twilio
        #auth_token = getattr(settings, "TWILIO_AUTH_TOKEN", None) or os.getenv("TWILIO_AUTH_TOKEN")
        #twilio_number = getattr(settings, "TWILIO_PHONE_NUMBER", None) or os.getenv("TWILIO_PHONE_NUMBER")
        #if not (account_sid and auth_token and twilio_number):a
          #  return JsonResponse({'error': 'Twilio credentials not configured.'}, status=500)
        # f"{inviter}!. Join here: http://chat-application-fj37.onrender.com/register/"
       ##try:
           # message = client.messages.create(
             #   from_=twilio_number,
           # )
           ## except Exception as e:
          #  return JsonResponse({'error': f'Failed to send SMS: {str(e)}'}, status=500)
    #else:
        #return JsonResponse({'error': 'Email or phone is required.'}, status=400)