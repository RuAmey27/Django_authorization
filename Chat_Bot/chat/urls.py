from django.urls import path
from . import views

urlpatterns = [
    path('chat-bot/', views.ChatBotView.as_view(), name='chat-bot'),  # Give it a meaningful name like 'chat-bot'
]
