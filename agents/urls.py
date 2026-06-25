from django.urls import path
from . import views

app_name = 'agents'

urlpatterns = [
    path('chat/', views.chat, name='chat'),
    path('api/chat/', views.api_chat, name='api_chat'),
]