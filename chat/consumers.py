import json
import base64
from django.core.files.base import ContentFile
from channels.generic.websocket import AsyncJsonWebsocketConsumer,WebsocketConsumer 
from channels.db import database_sync_to_async
from .models import ChatRoom, ChatMessage # Import your models here
from django.contrib.auth.models import User

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.other_user_id = self.scope['url_route']['kwargs']['other_user_id']

        self.user = await self.get_user_instance(self.user_id)
        self.other_user = await self.get_user_instance(self.other_user_id)

        if self.user and self.other_user:
            self.group_name = f'chat_{min(self.user_id, self.other_user_id)}_{max(self.user_id, self.other_user_id)}'
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            await self.send_existing_messages()
        else:
            await self.close()

    @database_sync_to_async
    def get_existing_messages(self):
        chatroom, _ = ChatRoom.objects.get_or_create(user1=self.user, user2=self.other_user)
        print("chatrooms",chatroom)
        messages = ChatMessage.objects.filter(room=chatroom).order_by('timestamp')
        print(messages)
        return [{
            'message': message.message,
            'sendername': message.sender.username,
            'is_read': message.is_read,
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'file_url': message.file.url if message.file else None
        } for message in messages]

    async def send_existing_messages(self):
        messages = await self.get_existing_messages()
        for message in messages:
            await self.send_json(message)

    @database_sync_to_async
    def get_user_instance(self, user_id):
        return User.objects.filter(id=user_id).first()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')
        sendername = data.get('sendername')
        file_data = data.get('file_data', None)
        file_name = data.get('file_name', None)


        print(f"Received message: {message} from {sendername}")

        if file_data:
            file_url = await self.save_message_with_file(sendername, message, file_data, file_name)
        else:
            file_url = None
            await self.save_message(sendername, message)

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sendername': sendername,
                'file_url': file_url
            }
        )

    async def chat_message(self, event):
        await self.send_json({
            'message': event['message'],
            'sendername': event['sendername'],
            'file_url': event.get('file_url', None)
        })

    @database_sync_to_async
    def save_message(self, sendername, message):
        chatroom, _ = ChatRoom.objects.get_or_create(user1=self.user, user2=self.other_user)
        sender = User.objects.get(username=sendername)
        ChatMessage.objects.create(
            room=chatroom,
            sender=sender,
            message=message,
            is_read=False
        )

    @database_sync_to_async
    def save_message_with_file(self, sendername, message, file_data, file_name):
        chatroom, _ = ChatRoom.objects.get_or_create(user1=self.user, user2=self.other_user)
        sender = User.objects.get(username=sendername)
        format, imgstr = file_data.split(';base64,')
        file_content = ContentFile(base64.b64decode(imgstr), name=file_name)
        message_instance = ChatMessage.objects.create(
            room=chatroom,
            sender=sender,
            message=message,
            is_read=False,
            file=file_content
        )
        return message_instance.file.url if message_instance.file else None
 