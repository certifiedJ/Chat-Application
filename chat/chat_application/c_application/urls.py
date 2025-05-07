from django.urls import path
from . import views

urlpatterns = [
    path('chat/<int:recipient_id>/', views.chat_view, name='chat'),
    path('chat/', views.chat_home, name='chat_home'),
    path('register/', views.registration_view, name='register'),
    path('fetch_messages/', views.fetch_messages, name='fetch_messages')
]