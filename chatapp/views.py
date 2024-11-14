from django.shortcuts import render
from django.db.models import Q
from .models import Chat
from user.models import Users
from .serializer import ChatSerializer
from user.serializers import UserSerializer
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response


# Create your views here.



class ChatHistorysView(generics.ListAPIView):
    serializer_class = ChatSerializer

    def get_queryset(self):
        sender_id = self.request.user.id
        receiver_id = self.kwargs['receiver_id']

        if sender_id == int(receiver_id):
            return Chat.objects.none()
        
        thread_name = f"chat_{min(sender_id, receiver_id)}_{max(sender_id, receiver_id)}"

        queryset = Chat.objects.filter(thread_name=thread_name).order_by('date')

        return queryset
    




class ChatUserListView(APIView):

    def get(self, request):
        current_user = request.user
        chat_users = Chat.objects.filter(
            Q(sender=current_user) | Q(receiver=current_user)
        ).values_list('sender', 'receiver').distinct()

        user_ids = set()
        for sender_id, receiver_id in chat_users:
            if sender_id != current_user.id:
                user_ids.add(sender_id)
            if receiver_id != current_user.id:
                user_ids.add(receiver_id)

        users = Users.objects.filter(id__in=user_ids)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
