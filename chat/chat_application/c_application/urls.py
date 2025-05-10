from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('chat/<int:recipient_id>/', views.chat_view, name='chat'),
    path('chat/', views.chat_home, name='chat_home'),
    path('register/', views.registration_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('fetch_messages/', views.fetch_messages, name='fetch_messages')
]