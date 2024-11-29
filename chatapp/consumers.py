
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
            await self.close()
            return
        
        self.room_name = f"chat_{min(self.sender.id, self.receiver.id)}_{max(self.sender.id, self.receiver.id)}"
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code_code):
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
                'message': message,
                'sender_id' : self.sender.id
            }
        )

    @database_sync_to_async
    def save_message(self, message):
        Chat.objects.create(
            sender=self.sender , receiver =self.receiver, message = message, thread_name = self.room_name
        )

    
    async def chat_message(self, event):
        message = event['message']
        sender_id = event['sender_id']
        await self.send(text_data=json.dumps({
            'message':message,
            'sender_id': sender_id,
        }))






class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_authenticated:
            self.user = self.scope["user"]
            self.group_name = f"user_{self.user.id}_notifications"

            # Add the user to a notifications group
            try:
            # Add the user to a notifications group
                await self.channel_layer.group_add(
                    self.group_name,
                    self.channel_name
                )
                
            except Exception as e:
                print(f"Error adding channel to group: {e}")


            await self.accept()
        else:
            await self.close()
        
        

    async def disconnect(self, close_code):
        # Leave the notifications group
        if self.scope["user"].is_authenticated:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )


    async def receive(self, text_data):
        # WebSocket message received
        data = json.loads(text_data)
        # Process received data if needed (e.g., mark notifications as read)

    async def send_notification(self, event):
        """Send notification to WebSocket."""

        await self.send(text_data=json.dumps({
            "type": event["type"],
            "message": event["message"]
        }))
