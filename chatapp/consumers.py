
import json
from channels.generic.websocket import AsyncWebsocketConsumer 
from channels.db import database_sync_to_async
from .models import Chat
from user.models import Users
import urllib.parse


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.receiver_id = self.scope['url_route']['kwargs']['receiver_id']
        self.sender = self.scope['user']
        
        try:
            self.receiver = await database_sync_to_async(Users.objects.get)(id=self.receiver_id)
        except Users.DoesNotExist:
            print('errrrro')
            await self.close()
            return
        
        self.room_name = f"chat_{min(self.sender.id, self.receiver.id)}_{max(self.sender.id, self.receiver.id)}"
        self.room_group_name = f'chat_{self.room_name}'

        print(self.room_group_name, self.room_name, 'rooooooooooooooooooooooooo')


        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code_code):
        print('heyeyey')
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.save_message(message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    @database_sync_to_async
    def save_message(self, message):
        Chat.objects.create(
            sender=self.sender , receiver =self.receiver, message = message, thread_name = self.room_name
        )

    
    async def chat_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message':message
        }))