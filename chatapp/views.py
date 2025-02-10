from django.shortcuts import render
from django.db.models import Q, Max
from .models import Chat
from user.models import Users
from .serializer import *
from user.serializers import UserSerializer, ListUsersSeralizer
from rest_framework import status, generics, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from QA.pagination import MessagePagination


#  view to fetch chat history between two users
class ChatHistorysView(generics.ListAPIView):
    pagination_class = MessagePagination
    serializer_class = ChatSerializer

    def get_queryset(self):
        sender_id = self.request.user.id
        receiver_id = self.kwargs['receiver_id']

        if sender_id == int(receiver_id):
            return Chat.objects.none()
        
        thread_name = f"chat_{min(sender_id, receiver_id)}_{max(sender_id, receiver_id)}"
        queryset = Chat.objects.filter(thread_name=thread_name).order_by('-date')
        return queryset 
    



# to list all users the current user has chatted with
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
        
        serializer = ListUsersSeralizer(users, many=True, context={'request': request})
        return Response(serializer.data)


# to fetch details of a specific user by user_id
class specificUserDetails(APIView):
    def get(self, request, user_id):
        user = get_object_or_404(Users, id=user_id)
        
        serializer = ListUsersSeralizer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    




class NotificationHistoryView(generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        print(self.request.user)
        return Notification.objects.filter(receiver = self.request.user.id).order_by('-id')
    