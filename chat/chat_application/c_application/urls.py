from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('chat/<int:recipient_id>/', views.chat_view, name='chat'),
    path('chat/', views.chat_home, name='chat_home'),
    path('register/', views.registration_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('fetch_messages/', views.fetch_messages, name='fetch_messages'),
    path('chat/typing/<int:recipient_id>/', views.set_typing, name='set_typing'),
    path('chat/is_typing/<int:recipient_id>/', views.is_typing, name='is_typing'),
    path('rooms/<int:room_id>/', views.room_detail, name='room_detail'),
    path('rooms/', views.room_list, name='room_list'),
    path('rooms/<int:room_id>/delete/', views.delete_room, name='delete_room'),
    path('submit_feedback/', views.submit_feedback, name='submit_feedback'),
    path('react_to_message/', views.react_to_message, name='react_to_message'),
    path('', views.home, name='home'),
]