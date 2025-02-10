from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .models import * 
from .serializer import *
from rest_framework import viewsets
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView, RetrieveAPIView, DestroyAPIView, UpdateAPIView
from rest_framework import filters
from rest_framework.permissions import AllowAny

from user.models import Users
from user.serializers import UserSerializer

from QA.serializer import QuestionSerializer, AnswerSerializer
from QA.models import Question, Answers

from rewards.models import *
from rewards.serializers import ProductSerializer

from .permission import IsSuperUser
from QA.pagination import AdminListPagination

from chatapp.models import Notification

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


# to mange tags CRUD oprtn
class ManageTag(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by('-id')
    serializer_class = TagSerializer
    pagination_class = AdminListPagination
    permission_classes = [IsSuperUser] 
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        queryset = Tag.objects.all().order_by('-id')
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset
    

# list all users except superuser
class UserList(ListAPIView):
    serializer_class = UserRetriUpdate
    pagination_class = AdminListPagination 
    permission_classes = [IsSuperUser] 
    def get_queryset(self):
        queryset = Users.objects.filter(is_superuser=False).order_by('-id')
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(username__icontains=search)
        return queryset
    
# retrive a specific user
class UserManage(RetrieveUpdateAPIView):
    queryset = Users.objects.all().order_by('-id')
    serializer_class = UserRetriUpdate
    permission_classes = [IsSuperUser] 
    lookup_field = 'id'
    def get_queryset(self):
        return Users.objects.filter(is_superuser=False)
    
# list all questions
class ListQuestions(ListAPIView):
    serializer_class = QuestionSerializer
    pagination_class = AdminListPagination
    permission_classes = [IsSuperUser] 

    def get_queryset(self):
        queryset =  Question.objects.all().order_by('-id')
        search = self.request.query_params.get('search', None)

        if search:
            queryset = queryset.filter(title__icontains=search)

        return queryset
    
# list all answers
class ListAnswers(ListAPIView):
    serializer_class = AnswerSerializer
    permission_classes = [IsSuperUser] 

    def get_queryset(self):
        return Answers.objects.all()
    
# retrive a specific question by ID
class AdminQuestionDetailView(RetrieveAPIView):
    queryset = Question.objects.all()
    serializer_class =  QuestionSerializer
    permission_classes = [IsSuperUser] 
    lookup_field='id'

# list all answer for a specific question 
class AdminQuestionAnswerView(ListAPIView):
    serializer_class = AnswerSerializer
    permission_classes = [IsSuperUser] 

    def get_queryset(self):
        question_id = self.kwargs.get('id')
        return  Answers.objects.filter(question_id=question_id)
    
# Delete a question by ID
class DeleteQuestionView(DestroyAPIView):
    queryset = Question.objects.all()
    permission_classes = [IsSuperUser] 
    lookup_field = 'id'

    def delete(self, request, *args, **kwargs):
        question_id = kwargs.get('id')
        print(f"Deleting question with ID: {question_id}")
        return super().delete(request, *args, **kwargs)
    
    
# Delete an answer and update the question's answer count
class DeleteAnswerView(DestroyAPIView):
    queryset = Answers.objects.all()
    permission_classes = [IsSuperUser] 
    lookup_field = 'id'

    def delete(self, request, *args, **kwargs):
        answer_id = kwargs.get('id')
        answer = self.get_object()
        question = answer.question
        if question:
            question.answer_count = max(0, question.answer_count - 1) 
            question.save()
        print(f'Deleting answer with id: {answer_id}')
        return super().delete(request, *args, **kwargs)
    

# block and unblock a user
class BlockUserView(UpdateAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSuperUser]


    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_blocked = not user.is_blocked
        user.is_active = not user.is_active
        user.save()

        status_message = "blocked" if user.is_blocked else "unblocked" 
        return Response({"message": f"User has been {status_message} successfully."},status=status.HTTP_200_OK)


# mange product CRUD oprtion
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-id')
    serializer_class = ProductSerializer
    permission_classes = [IsSuperUser]
    pagination_class = AdminListPagination


# list all orders
class OrdersList(ListAPIView):
    queryset = Order.objects.all().order_by('order_date')
    serializer_class = OrderListSerializer 
    permission_classes = [IsSuperUser]

# Retrieve details of a specific order
class OrderRetriveView(RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderListSerializer
    lookup_field = 'id' 
    

#  Update order status and create a notification
class OrderStatusUpdateView(UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderStatusUpdateSerializer
    permission_classes = [IsSuperUser] 
    lookup_field = 'id'

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.status == 'Canceled':
            return Response({"detail": "Cannot update an order with status 'Canceled'."}, status=status.HTTP_400_BAD_REQUEST)
        
        new_status = request.data.get('status')
        if new_status == 'Canceled':
            if instance.product:
                instance.product.quantity += 1
                instance.product.save()

        response = super().partial_update(request, *args, **kwargs)

        self.create_notification(instance, new_status)

        return response
    
    def create_notification(self, order, new_status):
        notification_message = f"Your order #{order.id} status has been updated to '{new_status}'."

        notification = Notification.objects.create(sender=self.request.user, receiver=order.user, notification_type='order_status', message=notification_message)

        channel_layer = get_channel_layer()
        group_name = f"user_{order.user.id}_notifications"

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "send_notification",
                "message": notification.message,
            }
        )