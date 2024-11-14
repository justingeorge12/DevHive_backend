from rest_framework import serializers
from .models import Chat
from user.models import Users

class ChatSerializer(serializers.ModelSerializer):
    sender_id = serializers.IntegerField(source='sender.id', read_only=True)
    sender = serializers.StringRelatedField()
    receiver = serializers.StringRelatedField()  

    class Meta:
        model = Chat
        fields = ['sender_id','sender', 'receiver', 'message', 'thread_name', 'date', 'read']
        read_only_fields = ['date']



        