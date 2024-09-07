from django.urls import path
from .consumers import ChatConsumer,VideoChatConsumer


websocket_urlpatterns = [
    path('ws/chat/<int:user_id>/<int:other_user_id>', ChatConsumer.as_asgi()),
    #   path('ws/video-chat/<int:user_id>/', VideoChatConsumer.as_asgi()),
    
]